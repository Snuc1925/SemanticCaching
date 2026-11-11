"""Classifier dạng rule (plan mục 4.8, 4.10). Không gọi LLM; cấu hình trong configs/classifier.yaml."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from functools import lru_cache

import numpy as np

from . import embeddings
from .config import classifier_config


@dataclass
class Classification:
    policy: str                       # NORMAL | SHORT_TTL | NO_CACHE | BYPASS
    reason: str
    intent: str = "default"
    intent_similarity: float = 0.0
    entities: dict[str, str] = field(default_factory=dict)


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower())


def _has(text: str, words: list[str]) -> str | None:
    for w in words:
        if w.lower() in text:
            return w
    return None


def cache_policy(question: str) -> tuple[str, str]:
    q = normalize(question)
    p = classifier_config()["policies"]
    if (w := _has(q, p["NO_CACHE"]["keywords"])):
        return "NO_CACHE", f"câu hỏi cá nhân (từ khoá '{w}')"
    b = p["BYPASS"]
    for s in b.get("starts_with", []):
        if q.startswith(s.lower()):
            return "BYPASS", f"câu nối tiếp (bắt đầu bằng '{s.strip()}')"
    if (w := _has(q, b.get("keywords", []))):
        return "BYPASS", f"câu nối tiếp (từ khoá '{w}')"
    if len(q.split()) < b.get("min_words", 0):
        return "BYPASS", f"câu quá ngắn (< {b['min_words']} từ)"
    if (w := _has(q, p["SHORT_TTL"]["keywords"])):
        return "SHORT_TTL", f"phụ thuộc thời điểm (từ khoá '{w}')"
    return "NORMAL", "câu hỏi tĩnh"


@lru_cache
def _intent_centroids() -> dict[str, np.ndarray]:
    ex = classifier_config()["intent"]["examples"]
    names, texts = [], []
    for name, items in ex.items():
        for t in items:
            names.append(name)
            texts.append(t)
    vecs, _, _ = embeddings.embed(texts)
    out: dict[str, np.ndarray] = {}
    for name in ex:
        m = np.mean([v for n, v in zip(names, vecs) if n == name], axis=0)
        out[name] = m / (np.linalg.norm(m) or 1.0)
    return out


def intent(vec: list[float]) -> tuple[str, float]:
    v = np.asarray(vec)
    best, score = "default", -1.0
    for name, c in _intent_centroids().items():
        s = float(v @ c)
        if s > score:
            best, score = name, s
    if score < classifier_config()["intent"]["min_similarity"]:
        return "default", score
    return best, score


def extract_entities(question: str) -> dict[str, str]:
    q = normalize(question)
    out: dict[str, str] = {}
    for etype, values in classifier_config()["entities"].items():
        # ưu tiên cụm dài hơn (vd "gói bạc" trước "bạc")
        matches = []
        for value, phrases in values.items():
            for ph in phrases:
                if re.search(rf"(?<!\w){re.escape(ph.lower())}(?!\w)", q):
                    matches.append((len(ph), value))
        if matches:
            out[etype] = max(matches)[1]
    return out


def classify(question: str, vec: list[float]) -> Classification:
    policy, reason = cache_policy(question)
    name, sim = intent(vec)
    return Classification(policy, reason, name, sim, extract_entities(question))
