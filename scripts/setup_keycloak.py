"""Cấu hình Keycloak từ data/pilot/acl.yaml: realm, role, client, resource (= collection), policy, permission, user.

Chạy lại được nhiều lần: realm bị XOÁ rồi tạo lại.
    .venv/bin/python scripts/setup_keycloak.py [--acl data/pilot/acl.yaml] [--keep]
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

import httpx
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
from app.config import env, settings  # noqa: E402

FRONTEND_ORIGIN = "http://localhost:5173"


class KC:
    def __init__(self):
        self.base = env().keycloak_url.rstrip("/")
        self.http = httpx.Client(timeout=30)
        r = self.http.post(f"{self.base}/realms/master/protocol/openid-connect/token", data={
            "client_id": "admin-cli", "grant_type": "password",
            "username": env().keycloak_admin, "password": env().keycloak_admin_password})
        r.raise_for_status()
        self.h = {"Authorization": f"Bearer {r.json()['access_token']}"}

    def req(self, method, path, ok=(200, 201, 204), **kw):
        r = self.http.request(method, f"{self.base}/admin/realms{path}", headers=self.h, **kw)
        if r.status_code not in ok:
            raise RuntimeError(f"{method} {path} -> {r.status_code}: {r.text[:300]}")
        return r


def wait_keycloak():
    base = env().keycloak_url.rstrip("/")
    for _ in range(60):
        try:
            if httpx.get(f"{base}/realms/master", timeout=3).status_code == 200:
                return
        except httpx.HTTPError:
            pass
        time.sleep(2)
    raise SystemExit("Keycloak chưa sẵn sàng")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--acl", default=str(ROOT / settings()["data_dir"] / "acl.yaml"))
    args = ap.parse_args()
    acl = yaml.safe_load(open(args.acl, encoding="utf-8"))
    kcs = settings()["keycloak"]
    realm = acl["realm"]
    wait_keycloak()
    kc = KC()

    # 1. Realm (xoá + tạo lại)
    kc.req("DELETE", f"/{realm}", ok=(204, 404))
    kc.req("POST", "", json={
        "realm": realm, "enabled": True, "displayName": "Semantic Cache Demo",
        "adminEventsEnabled": True, "adminEventsDetailsEnabled": True,
        "accessTokenLifespan": 900, "ssoSessionIdleTimeout": 3600,
        "internationalizationEnabled": True, "supportedLocales": ["vi", "en"], "defaultLocale": "vi",
    })
    R = f"/{realm}"
    print(f"realm '{realm}' created")

    # 2. Cho phép thuộc tính user tuỳ ý (region) - Keycloak 24+ mặc định chặn thuộc tính không khai báo
    prof = kc.req("GET", f"{R}/users/profile").json()
    prof["unmanagedAttributePolicy"] = "ENABLED"
    kc.req("PUT", f"{R}/users/profile", json=prof)

    # 3. Realm roles
    for role in acl["roles"]:
        kc.req("POST", f"{R}/roles", json={"name": role["name"], "description": role.get("description", "")})
    roles = {r["name"]: r for r in kc.req("GET", f"{R}/roles").json()}

    # 4. Client frontend (public, PKCE)
    kc.req("POST", f"{R}/clients", json={
        "clientId": kcs["frontend_client"], "name": "Semantic Cache Web", "publicClient": True,
        "standardFlowEnabled": True, "directAccessGrantsEnabled": True,
        "redirectUris": [f"{FRONTEND_ORIGIN}/*"], "webOrigins": [FRONTEND_ORIGIN],
        "attributes": {"pkce.code.challenge.method": "S256", "post.logout.redirect.uris": f"{FRONTEND_ORIGIN}/*"},
    })

    # 5. Client backend (confidential, service account, authorization services)
    kc.req("POST", f"{R}/clients", json={
        "clientId": kcs["backend_client"], "name": "Semantic Cache Backend", "publicClient": False,
        "secret": kcs["backend_client_secret"], "serviceAccountsEnabled": True,
        "authorizationServicesEnabled": True, "standardFlowEnabled": False, "directAccessGrantsEnabled": False,
    })
    clients = kc.req("GET", f"{R}/clients", params={"clientId": kcs["backend_client"]}).json()
    cu = clients[0]["id"]
    # claim "region" từ thuộc tính user -> dùng cho regex policy (ABAC)
    kc.req("POST", f"{R}/clients/{cu}/protocol-mappers/models", json={
        "name": "region", "protocol": "openid-connect", "protocolMapper": "oidc-usermodel-attribute-mapper",
        "config": {"user.attribute": "region", "claim.name": "region", "jsonType.label": "String",
                   "access.token.claim": "true", "id.token.claim": "true", "userinfo.token.claim": "true"}})

    # 6. Quyền cho service account của backend (đọc/sửa user, đánh giá policy, đọc admin events)
    sa = kc.req("GET", f"{R}/clients/{cu}/service-account-user").json()
    rm = kc.req("GET", f"{R}/clients", params={"clientId": "realm-management"}).json()[0]["id"]
    rm_roles = {r["name"]: r for r in kc.req("GET", f"{R}/clients/{rm}/roles").json()}
    wanted = ["view-users", "query-users", "manage-users", "view-realm", "view-events",
              "view-clients", "manage-clients", "view-authorization", "manage-authorization"]
    kc.req("POST", f"{R}/users/{sa['id']}/role-mappings/clients/{rm}", json=[rm_roles[n] for n in wanted])

    # 7. Authorization: xoá mặc định, tạo resource/policy/permission
    A = f"{R}/clients/{cu}/authz/resource-server"
    for p in kc.req("GET", f"{A}/policy", params={"max": 100}).json():
        kc.req("DELETE", f"{A}/policy/{p['id']}", ok=(204, 404))
    for res in kc.req("GET", f"{A}/resource", params={"max": 100}).json():
        kc.req("DELETE", f"{A}/resource/{res['_id']}", ok=(204, 404))

    res_ids = {}
    for cid, c in acl["collections"].items():
        r = kc.req("POST", f"{A}/resource", json={
            "name": f"collection:{cid}", "displayName": c.get("title", cid),
            "type": "urn:semcache:collection", "attributes": {"collection": [cid]}}).json()
        res_ids[cid] = r["_id"]

    pol_ids = {}
    for p in acl["policies"]:
        if p["type"] == "role":
            body = {"name": p["name"], "logic": "POSITIVE", "decisionStrategy": "UNANIMOUS", "fetchRoles": True,
                    "roles": [{"id": roles[n]["id"], "required": False} for n in p["roles"]]}
            r = kc.req("POST", f"{A}/policy/role", json=body).json()
        elif p["type"] == "regex":
            body = {"name": p["name"], "logic": "POSITIVE", "targetClaim": p["claim"], "pattern": p["pattern"]}
            r = kc.req("POST", f"{A}/policy/regex", json=body).json()
        else:
            raise ValueError(p["type"])
        pol_ids[p["name"]] = r["id"]

    for cid, c in acl["collections"].items():
        kc.req("POST", f"{A}/permission/resource", json={
            "name": f"read {cid}", "decisionStrategy": "UNANIMOUS",
            "resources": [res_ids[cid]], "policies": [pol_ids[n] for n in c["policies"]]})

    # 8. Users
    for u in acl["users"]:
        first, _, last = u.get("name", u["username"]).partition(" ")
        kc.req("POST", f"{R}/users", json={
            "username": u["username"], "enabled": True, "emailVerified": True,
            "email": f"{u['username']}@saomai.local", "firstName": first or u["username"], "lastName": last or "-",
            "attributes": {k: [v] for k, v in (u.get("attributes") or {}).items()},
            "credentials": [{"type": "password", "value": acl["default_password"], "temporary": False}]})
        uid = kc.req("GET", f"{R}/users", params={"username": u["username"], "exact": "true"}).json()[0]["id"]
        kc.req("POST", f"{R}/users/{uid}/role-mappings/realm", json=[roles[n] for n in u["roles"]])
    print(f"{len(acl['users'])} users, {len(acl['collections'])} collections configured")

    # 9. Kiểm tra: đánh giá quyền từng user bằng chính adapter của backend
    from app.iam.base import UserContext
    from app.iam.keycloak import KeycloakAccessControl, KeycloakAdmin

    adapter = KeycloakAccessControl(KeycloakAdmin())
    print("\nQuyền đọc collection theo Keycloak (kiểm tra):")
    for u in acl["users"]:
        info = adapter.admin.find_user(u["username"])
        cols = adapter.list_accessible_collections(UserContext(info["id"], u["username"]))
        print(f"  {u['username']:10s} -> {sorted(cols)}")


if __name__ == "__main__":
    main()
