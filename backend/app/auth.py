"""Xác thực token Keycloak (OIDC) do frontend gửi lên."""
from __future__ import annotations

from functools import lru_cache

import jwt
from fastapi import Depends, HTTPException, Query, Request

from .config import env, settings
from .iam.base import UserContext


@lru_cache
def _jwks() -> jwt.PyJWKClient:
    realm = settings()["keycloak"]["realm"]
    return jwt.PyJWKClient(f"{env().keycloak_url}/realms/{realm}/protocol/openid-connect/certs", cache_keys=True)


def issuer() -> str:
    return f"{env().keycloak_public_url}/realms/{settings()['keycloak']['realm']}"


def decode(token: str) -> UserContext:
    try:
        key = _jwks().get_signing_key_from_jwt(token).key
        claims = jwt.decode(token, key, algorithms=["RS256"], issuer=issuer(), options={"verify_aud": False})
    except Exception as e:  # noqa: BLE001
        raise HTTPException(401, f"Token không hợp lệ: {e}") from e
    if claims.get("azp") != settings()["keycloak"]["frontend_client"]:
        raise HTTPException(401, "Token không phải của frontend client")
    roles = tuple((claims.get("realm_access") or {}).get("roles", []))
    return UserContext(claims["sub"], claims.get("preferred_username", claims["sub"]), roles, claims.get("name", ""))


def current_user(request: Request) -> UserContext:
    h = request.headers.get("Authorization", "")
    if not h.startswith("Bearer "):
        raise HTTPException(401, "Thiếu token")
    return decode(h[7:])


def console_user(user: UserContext = Depends(current_user)) -> UserContext:
    if settings()["keycloak"]["console_role"] not in user.roles:
        raise HTTPException(403, "Cần role ops_admin để vào Console")
    return user


def console_user_from_query(token: str = Query(...)) -> UserContext:
    """SSE (EventSource) không gửi được header -> token qua query string."""
    user = decode(token)
    if settings()["keycloak"]["console_role"] not in user.roles:
        raise HTTPException(403, "Cần role ops_admin")
    return user
