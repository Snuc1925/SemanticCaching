"""Adapter Keycloak Authorization Services.

- Mỗi collection = 1 resource "collection:<id>" trên client semcache-backend.
- Đánh giá quyền bằng API policy evaluate (giống PermRAG), dùng service account của backend
  thay vì xin admin token mỗi lần (PermRAG xin token cho từng lần check -> chậm).
- Sự kiện thay đổi quyền đọc từ Keycloak Admin Events (poll).
"""
from __future__ import annotations

import hashlib
import threading
import time
from datetime import datetime, timezone

import httpx

from ..config import env, settings
from .base import AccessChangeEvent, AccessControlBase, ChangeEventSource, UserContext

RESOURCE_PREFIX = "collection:"


class KeycloakAdmin:
    """Gọi Keycloak Admin REST API bằng token của service account (client credentials)."""

    def __init__(self, realm: str | None = None, client_id: str | None = None, client_secret: str | None = None):
        kc = settings()["keycloak"]
        self.base = env().keycloak_url.rstrip("/")
        self.realm = realm or kc["realm"]
        self.client_id = client_id or kc["backend_client"]
        self.client_secret = client_secret or kc["backend_client_secret"]
        self._token: str | None = None
        self._token_exp = 0.0
        self._lock = threading.Lock()
        self._http = httpx.Client(timeout=10)
        self._client_uuid: str | None = None

    # ---- token ----
    def token(self) -> str:
        with self._lock:
            if self._token and time.time() < self._token_exp - 30:
                return self._token
            r = self._http.post(
                f"{self.base}/realms/{self.realm}/protocol/openid-connect/token",
                data={"grant_type": "client_credentials", "client_id": self.client_id, "client_secret": self.client_secret},
            )
            r.raise_for_status()
            j = r.json()
            self._token, self._token_exp = j["access_token"], time.time() + j.get("expires_in", 60)
            return self._token

    def request(self, method: str, path: str, **kw) -> httpx.Response:
        url = f"{self.base}/admin/realms/{self.realm}{path}"
        r = self._http.request(method, url, headers={"Authorization": f"Bearer {self.token()}"}, **kw)
        r.raise_for_status()
        return r

    # ---- helpers ----
    def client_uuid(self) -> str:
        if not self._client_uuid:
            items = self.request("GET", "/clients", params={"clientId": self.client_id}).json()
            self._client_uuid = items[0]["id"]
        return self._client_uuid

    def find_user(self, username: str) -> dict | None:
        items = self.request("GET", "/users", params={"username": username, "exact": "true"}).json()
        return items[0] if items else None

    def list_users(self) -> list[dict]:
        return self.request("GET", "/users", params={"max": 500, "briefRepresentation": "false"}).json()

    def user_realm_roles(self, user_id: str) -> list[str]:
        return [r["name"] for r in self.request("GET", f"/users/{user_id}/role-mappings/realm").json()]

    def realm_role(self, name: str) -> dict:
        return self.request("GET", f"/roles/{name}").json()

    def set_realm_role(self, user_id: str, role: str, grant: bool) -> None:
        rep = self.realm_role(role)
        self.request("POST" if grant else "DELETE", f"/users/{user_id}/role-mappings/realm",
                     json=[{"id": rep["id"], "name": rep["name"]}])

    def evaluate(self, user_id: str, resource_names: list[str] | None = None) -> dict[str, bool]:
        """Đánh giá quyền đọc. resource_names=None -> đánh giá mọi resource."""
        cu = self.client_uuid()
        resources = []
        if resource_names:
            all_res = self.resources()
            resources = [{"_id": all_res[n], "name": n} for n in resource_names if n in all_res]
            if not resources:
                return {}
        body = {"userId": user_id, "clientId": cu, "resources": resources, "roleIds": [],
                "entitlements": False, "context": {"attributes": {}}}
        j = self.request("POST", f"/clients/{cu}/authz/resource-server/policy/evaluate", json=body).json()
        out: dict[str, bool] = {}
        for res in j.get("results", []):
            name = (res.get("resource") or {}).get("name", "")
            out[name] = res.get("status") == "PERMIT"
        return out

    _res_cache: dict[str, str] | None = None
    _res_cache_at = 0.0

    def resources(self) -> dict[str, str]:
        if self._res_cache is None or time.time() - self._res_cache_at > 60:
            cu = self.client_uuid()
            items = self.request("GET", f"/clients/{cu}/authz/resource-server/resource", params={"max": 1000}).json()
            self._res_cache = {i["name"]: i["_id"] for i in items}
            self._res_cache_at = time.time()
        return self._res_cache

    def admin_events(self, max_results: int = 200) -> list[dict]:
        return self.request("GET", "/admin-events", params={"max": max_results}).json()


class KeycloakAccessControl(AccessControlBase):
    namespace = "keycloak"

    def __init__(self, admin: KeycloakAdmin | None = None):
        self.admin = admin or KeycloakAdmin()

    def list_accessible_collections(self, user: UserContext) -> set[str]:
        decisions = self.admin.evaluate(user.user_id)
        return {n[len(RESOURCE_PREFIX):] for n, ok in decisions.items() if ok and n.startswith(RESOURCE_PREFIX)}

    def check_collections(self, user: UserContext, collections: set[str]) -> dict[str, bool]:
        if not collections:
            return {}
        try:
            decisions = self.admin.evaluate(user.user_id, [RESOURCE_PREFIX + c for c in sorted(collections)])
        except Exception:  # noqa: BLE001  - IAM lỗi -> từ chối (fail-closed, giống PermRAG)
            return {c: False for c in collections}
        return {c: decisions.get(RESOURCE_PREFIX + c, False) for c in collections}


# Loại tài nguyên trong admin events có thể làm thay đổi quyền.
_USER_SCOPED = {"REALM_ROLE_MAPPING", "CLIENT_ROLE_MAPPING", "GROUP_MEMBERSHIP", "USER"}
_GLOBAL = {"AUTHORIZATION_POLICY", "AUTHORIZATION_RESOURCE", "AUTHORIZATION_SCOPE", "AUTHORIZATION_RESOURCE_SERVER",
           "REALM_ROLE", "GROUP", "CLIENT_ROLE", "COMPONENT", "REALM"}


def _event_key(e: dict) -> str:
    """Keycloak 26.0 không trả "id" cho admin event -> khử trùng bằng khoá ghép từ nội dung."""
    if e.get("id"):
        return str(e["id"])
    rep = hashlib.sha1((e.get("representation") or "").encode()).hexdigest()[:10]
    return f"{e.get('time')}|{e.get('operationType')}|{e.get('resourceType')}|{e.get('resourcePath')}|{rep}"


class KeycloakEventSource(ChangeEventSource):
    def __init__(self, admin: KeycloakAdmin, since_ms: int):
        self.admin = admin
        self.last_ms = since_ms
        self._seen: set[str] = set()

    def poll(self) -> list[AccessChangeEvent]:
        raw = self.admin.admin_events()
        fresh = [e for e in raw if e.get("time", 0) >= self.last_ms and _event_key(e) not in self._seen]
        fresh.sort(key=lambda e: e["time"])
        out: list[AccessChangeEvent] = []
        for e in fresh:
            self._seen.add(_event_key(e))
            self.last_ms = max(self.last_ms, e["time"])
            rtype = e.get("resourceType", "")
            path = e.get("resourcePath", "") or ""
            when = datetime.fromtimestamp(e["time"] / 1000, tz=timezone.utc)
            op = e.get("operationType", "")
            if rtype in _USER_SCOPED and path.startswith("users/"):
                uid = path.split("/")[1]
                kind = "user_attribute" if rtype == "USER" else "role_mapping"
                out.append(AccessChangeEvent(when, kind, f"{op} {rtype} ({path})", user_ids=[uid], raw=e))
            elif rtype in _GLOBAL:
                out.append(AccessChangeEvent(when, "policy", f"{op} {rtype} ({path})", affects_all=True, raw=e))
        if len(self._seen) > 5000:
            self._seen = set(list(self._seen)[-1000:])
        return out
