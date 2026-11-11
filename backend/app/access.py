"""Access signature (plan mục 4.4): signature(u) = hash(scheme_version, sorted(collection có namespace)).

Hai user cùng signature <=> đọc được đúng cùng một tập tài liệu => dùng chung partition cache an toàn và đầy đủ.
Signature được cache trong Redis với TTL (chặn trên khi lỡ event); bị xoá ngay khi có event thay đổi quyền.
"""
from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass
from functools import lru_cache

from .clients import rds
from .config import settings
from .iam.base import AccessControlBase, UserContext
from .iam.keycloak import KeycloakAccessControl


@lru_cache
def adapter() -> AccessControlBase:
    return KeycloakAccessControl()


@dataclass
class Signature:
    signature: str
    collections: list[str]          # id collection (không namespace) dùng để lọc Qdrant
    computed_at: float
    from_cache: bool


def _key(user_id: str) -> str:
    return f"sig:user:{user_id}"


def compute_hash(namespaced: list[str]) -> str:
    v = settings()["access"]["signature_scheme_version"]
    return hashlib.sha256(f"v{v}|{','.join(sorted(namespaced))}".encode()).hexdigest()[:16]


def get(user: UserContext) -> Signature:
    raw = rds().get(_key(user.user_id))
    if raw:
        d = json.loads(raw)
        return Signature(d["signature"], d["collections"], d["computed_at"], True)
    return refresh(user)


def refresh(user: UserContext) -> Signature:
    ad = adapter()
    cols = sorted(ad.list_accessible_collections(user))
    sig = compute_hash([f"{ad.namespace}:{c}" for c in cols])
    now = time.time()
    rds().set(_key(user.user_id), json.dumps({"signature": sig, "collections": cols, "computed_at": now,
                                               "username": user.username}),
              ex=settings()["access"]["signature_ttl_seconds"])
    rds().hset("sig:known", user.user_id, json.dumps({"username": user.username, "signature": sig}))
    return Signature(sig, cols, now, False)


def invalidate(user_id: str) -> bool:
    return bool(rds().delete(_key(user_id)))


def invalidate_all() -> int:
    keys = list(rds().scan_iter("sig:user:*"))
    return rds().delete(*keys) if keys else 0


def partitions() -> dict[str, list[str]]:
    """signature -> danh sách username (theo lần tính gần nhất)."""
    out: dict[str, list[str]] = {}
    for _, v in rds().hgetall("sig:known").items():
        d = json.loads(v)
        out.setdefault(d["signature"], []).append(d["username"])
    return out
