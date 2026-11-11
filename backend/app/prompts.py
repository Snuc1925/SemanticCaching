"""Prompt nằm trong configs/prompts.yaml, không hard-code trong code."""
from __future__ import annotations

import hashlib
import json
import string
from functools import lru_cache

from .config import ROOT, load_yaml


class PromptError(ValueError):
    pass


@lru_cache
def _all() -> dict:
    return load_yaml(ROOT / "configs" / "prompts.yaml")


def get(name: str) -> dict:
    data = _all()
    if name not in data or not isinstance(data[name], dict):
        raise PromptError(f"Không có prompt '{name}' trong configs/prompts.yaml")
    return data[name]


def text(name: str) -> str:
    return str(_all()[name])


def variables(name: str) -> set[str]:
    p = get(name)
    out: set[str] = set()
    for part in ("system", "user"):
        for _, field, _, _ in string.Formatter().parse(p.get(part, "")):
            if field:
                out.add(field)
    return out


def render(name: str, **kwargs) -> tuple[str, str]:
    """Trả (system, user). Báo lỗi rõ ràng nếu thiếu biến."""
    missing = variables(name) - kwargs.keys()
    if missing:
        raise PromptError(f"Prompt '{name}' thiếu biến: {sorted(missing)}")
    p = get(name)
    return p.get("system", "").format(**kwargs), p.get("user", "").format(**kwargs)


def version(name: str) -> str:
    """Mã phiên bản = version chung + hash nội dung prompt. Đổi prompt -> đổi mã -> cache cũ thành MISS."""
    p = get(name)
    digest = hashlib.sha256(json.dumps(p, sort_keys=True, ensure_ascii=False).encode()).hexdigest()[:8]
    return f"v{_all().get('version', 1)}-{digest}"


def validate(required: dict[str, set[str]]) -> None:
    """Gọi lúc khởi động: kiểm tra mỗi prompt chỉ dùng các biến mà code sẽ truyền."""
    for name, provided in required.items():
        extra = variables(name) - provided
        if extra:
            raise PromptError(f"Prompt '{name}' dùng biến code không truyền: {sorted(extra)}")
