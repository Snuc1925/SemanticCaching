"""Gọi Gemini. Prompt lấy từ configs/prompts.yaml."""
from __future__ import annotations

import time
from dataclasses import dataclass

from . import prompts
from .clients import gemini_client
from .config import settings


@dataclass
class LLMResult:
    text: str
    tokens_in: int
    tokens_out: int
    latency_ms: float
    model: str
    prompt_version: str


def model() -> str:
    return settings()["models"]["llm"]


def cost_usd(tokens_in: int, tokens_out: int, embed_tokens: int = 0) -> float:
    p = settings()["pricing"]
    return (tokens_in * p["llm_input"] + tokens_out * p["llm_output"] + embed_tokens * p["embedding"]) / 1e6


def generate(prompt_name: str, **variables) -> LLMResult:
    from google.genai import types

    cfg = prompts.get(prompt_name)
    system, user = prompts.render(prompt_name, **variables)
    t0 = time.perf_counter()
    last_err: Exception | None = None
    for attempt in range(3):
        try:
            resp = gemini_client().models.generate_content(
                model=model(),
                contents=user,
                config=types.GenerateContentConfig(
                    system_instruction=system,
                    temperature=cfg.get("temperature", 0.2),
                    max_output_tokens=cfg.get("max_output_tokens", 800),
                ),
            )
            u = resp.usage_metadata
            return LLMResult(
                text=(resp.text or "").strip(),
                tokens_in=u.prompt_token_count or 0,
                tokens_out=u.candidates_token_count or 0,
                latency_ms=(time.perf_counter() - t0) * 1000,
                model=model(),
                prompt_version=prompts.version(prompt_name),
            )
        except Exception as e:  # noqa: BLE001
            last_err = e
            time.sleep(1.5 * (attempt + 1))
    raise RuntimeError(f"Gemini lỗi sau 3 lần thử: {last_err}")
