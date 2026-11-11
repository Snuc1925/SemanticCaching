"""Kiểm tra nhanh kết nối OpenAI (embedding) và Gemini (LLM).

Chạy:  .venv/bin/python scripts/check_apis.py [--env .env] [--model <gemini-model-id>]
Không in API key ra màn hình.
"""
import argparse
import math
import os
import sys
import time
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]


def check_openai(model: str) -> bool:
    from openai import OpenAI

    print(f"\n=== OpenAI embedding ({model}) ===")
    try:
        client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
        texts = [
            "Khách hàng được đổi trả trong bao nhiêu ngày?",
            "Tôi có thể trả lại hàng trong mấy ngày?",
            "Giá gói bảo hành mở rộng là bao nhiêu?",
        ]
        t0 = time.perf_counter()
        resp = client.embeddings.create(model=model, input=texts)
        ms = (time.perf_counter() - t0) * 1000
        vecs = [d.embedding for d in resp.data]

        def cos(a, b):
            dot = sum(x * y for x, y in zip(a, b))
            return dot / (math.sqrt(sum(x * x for x in a)) * math.sqrt(sum(y * y for y in b)))

        print(f"OK  dim={len(vecs[0])}  latency={ms:.0f}ms  tokens={resp.usage.total_tokens}")
        print(f"cos(paraphrase)      = {cos(vecs[0], vecs[1]):.3f}   (kỳ vọng cao)")
        print(f"cos(khác chủ đề)     = {cos(vecs[0], vecs[2]):.3f}   (kỳ vọng thấp hơn)")
        return True
    except Exception as e:  # noqa: BLE001
        print(f"FAIL {type(e).__name__}: {e}")
        return False


def check_gemini(model: str | None) -> bool:
    from google import genai

    print("\n=== Gemini ===")
    try:
        client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
        names = [m.name for m in client.models.list()]
        lite = [n for n in names if "flash" in n and "lite" in n]
        print(f"Số model truy cập được: {len(names)}")
        print("Model flash-lite:", ", ".join(sorted(lite)) or "(không có)")

        if model is None:
            preferred = [n for n in lite if "3.5" in n] or lite
            if not preferred:
                print("FAIL không tìm thấy model flash-lite nào")
                return False
            model = sorted(preferred)[-1]
        model = model.removeprefix("models/")
        print(f"Dùng model: {model}")

        t0 = time.perf_counter()
        resp = client.models.generate_content(
            model=model,
            contents="Trả lời ngắn gọn bằng tiếng Việt trong 1 câu: semantic cache là gì?",
        )
        ms = (time.perf_counter() - t0) * 1000
        u = resp.usage_metadata
        print(f"OK  latency={ms:.0f}ms  tokens in={u.prompt_token_count} out={u.candidates_token_count}")
        print("Trả lời:", (resp.text or "").strip())
        return True
    except Exception as e:  # noqa: BLE001
        print(f"FAIL {type(e).__name__}: {e}")
        return False


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--env", default=str(ROOT / ".env"))
    ap.add_argument("--model", default=os.environ.get("LLM_MODEL"))
    ap.add_argument("--embedding-model", default="text-embedding-3-small")
    args = ap.parse_args()

    if not load_dotenv(args.env):
        print(f"Không đọc được {args.env}")
        return 1
    missing = [k for k in ("OPENAI_API_KEY", "GEMINI_API_KEY") if not os.environ.get(k)]
    if missing:
        print("Thiếu biến:", ", ".join(missing))
        return 1

    ok_openai = check_openai(args.embedding_model)
    ok_gemini = check_gemini(args.model or os.environ.get("LLM_MODEL"))
    print(f"\nKết quả: OpenAI={'OK' if ok_openai else 'FAIL'}  Gemini={'OK' if ok_gemini else 'FAIL'}")
    return 0 if (ok_openai and ok_gemini) else 1


if __name__ == "__main__":
    sys.exit(main())
