"""Nạp cấu hình: .env (secret, địa chỉ hạ tầng) + configs/settings.yaml (tham số hệ thống)."""
from __future__ import annotations

import os
import re
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[2]          # .../src
load_dotenv(ROOT / ".env")

_VAR = re.compile(r"\$\{([A-Z0-9_]+)(?::([^}]*))?\}")


def _expand(value: Any) -> Any:
    """Thay ${VAR:default} bằng biến môi trường."""
    if isinstance(value, str):
        return _VAR.sub(lambda m: os.environ.get(m.group(1), m.group(2) or ""), value)
    if isinstance(value, dict):
        return {k: _expand(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_expand(v) for v in value]
    return value


def load_yaml(path: Path) -> dict:
    with open(path, encoding="utf-8") as f:
        return _expand(yaml.safe_load(f) or {})


@dataclass(frozen=True)
class Env:
    openai_api_key: str
    gemini_api_key: str
    postgres_dsn: str
    qdrant_url: str
    redis_url: str
    keycloak_url: str          # địa chỉ backend gọi tới Keycloak
    keycloak_public_url: str   # địa chỉ trình duyệt thấy (issuer trong token)
    keycloak_admin: str
    keycloak_admin_password: str


@lru_cache
def env() -> Env:
    g = os.environ.get
    dsn = (
        f"postgresql://{g('POSTGRES_USER', 'semcache')}:{g('POSTGRES_PASSWORD', 'semcache')}"
        f"@{g('POSTGRES_HOST', 'localhost')}:{g('POSTGRES_PORT', '5432')}/{g('POSTGRES_DB', 'semcache')}"
    )
    return Env(
        openai_api_key=g("OPENAI_API_KEY", ""),
        gemini_api_key=g("GEMINI_API_KEY", ""),
        postgres_dsn=dsn,
        qdrant_url=g("QDRANT_URL", "http://localhost:6333"),
        redis_url=g("REDIS_URL", "redis://localhost:6379/0"),
        keycloak_url=g("KEYCLOAK_URL", "http://localhost:8080"),
        keycloak_public_url=g("KEYCLOAK_PUBLIC_URL", g("KEYCLOAK_URL", "http://localhost:8080")),
        keycloak_admin=g("KEYCLOAK_ADMIN", "admin"),
        keycloak_admin_password=g("KEYCLOAK_ADMIN_PASSWORD", "admin"),
    )


@lru_cache
def settings() -> dict:
    return load_yaml(ROOT / "configs" / "settings.yaml")


@lru_cache
def classifier_config() -> dict:
    return load_yaml(ROOT / "configs" / "classifier.yaml")


def data_dir() -> Path:
    return ROOT / settings()["data_dir"]
