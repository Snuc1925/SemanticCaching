"""Embedding qua OpenAI, có cache theo nội dung trong Redis (giảm chi phí khi chạy lại test/workload)."""
from __future__ import annotations

import hashlib
import json

import numpy as np

from .clients import openai_client, rds
from .config import settings

_TTL = 30 * 24 * 3600


def model() -> str:
    return settings()["models"]["embedding"]


def _key(text: str) -> str:
    return f"emb:{model()}:{hashlib.sha1(text.encode()).hexdigest()}"


def embed(texts: list[str]) -> tuple[list[list[float]], int, bool]:
    """Trả (vectors đã chuẩn hoá L2, số token tính phí, có lấy hết từ cache không)."""
    r = rds()
    cached = r.mget([_key(t) for t in texts]) if texts else []
    out: list[list[float] | None] = [json.loads(c) if c else None for c in cached]
    missing = [i for i, v in enumerate(out) if v is None]
    tokens = 0
    if missing:
        resp = openai_client().embeddings.create(model=model(), input=[texts[i] for i in missing])
        tokens = resp.usage.total_tokens
        pipe = r.pipeline()
        for i, d in zip(missing, resp.data):
            v = np.asarray(d.embedding, dtype=np.float32)
            v = (v / (np.linalg.norm(v) or 1.0)).tolist()
            out[i] = v
            pipe.set(_key(texts[i]), json.dumps(v), ex=_TTL)
        pipe.execute()
    return out, tokens, not missing  # type: ignore[return-value]


def embed_one(text: str) -> tuple[list[float], int, bool]:
    vecs, tokens, hit = embed([text])
    return vecs[0], tokens, hit


def dim() -> int:
    return len(embed_one("dimension probe")[0])
