"""Unit test không cần API ngoài (OpenAI/Gemini/Keycloak). Chạy: .venv/bin/pytest -q tests"""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))

from app import audit, prompts  # noqa: E402
from app.access import compute_hash  # noqa: E402
from app.chunking import chunk_document  # noqa: E402
from app.classifier import cache_policy, extract_entities  # noqa: E402
from app.documents import parse_file  # noqa: E402
from app.iam.keycloak import _event_key  # noqa: E402

DOCS = Path(__file__).resolve().parents[1] / "data" / "pilot" / "docs"


# ---- chunking
def test_chunks_never_cross_documents_and_carry_version():
    meta, body = parse_file(DOCS / "return_policy.v1.md")
    chunks = chunk_document(meta["doc_id"], 1, meta["collection"], meta["title"], body)
    assert chunks
    assert all(c.doc_id == "return_policy" and c.version == 1 and c.collection == "public" for c in chunks)
    assert all(c.embed_text.startswith("[Chính sách đổi trả hàng") for c in chunks)


def test_chunk_id_changes_with_version():
    meta, body = parse_file(DOCS / "return_policy.v1.md")
    a = chunk_document("return_policy", 1, "public", meta["title"], body)
    b = chunk_document("return_policy", 2, "public", meta["title"], body)
    assert {c.chunk_id for c in a}.isdisjoint({c.chunk_id for c in b})


def test_fact_and_condition_stay_together():
    meta, body = parse_file(DOCS / "vip_return_exception.v1.md")
    chunks = chunk_document(meta["doc_id"], 1, meta["collection"], meta["title"], body)
    assert any("VIP" in c.text and "33 ngày" in c.text for c in chunks)


# ---- classifier
@pytest.mark.parametrize("q,policy", [
    ("Chính sách đổi trả trong bao nhiêu ngày?", "NORMAL"),
    ("Đơn hàng của tôi đang ở đâu rồi?", "NO_CACHE"),
    ("Khuyến mãi tháng này có gì?", "SHORT_TTL"),
    ("Thế còn hàng điện tử thì sao?", "BYPASS"),
    ("Còn gói Vàng?", "BYPASS"),
])
def test_cache_policy(q, policy):
    assert cache_policy(q)[0] == policy


def test_entities_distinguish_hard_negatives():
    assert extract_entities("Giá gói bảo hành mở rộng Bạc là bao nhiêu?") == {"package": "bac"}
    assert extract_entities("Giá gói bảo hành mở rộng Vàng là bao nhiêu?") == {"package": "vang"}
    assert extract_entities("Khách VIP được đổi trả trong bao lâu?") == {"tier": "vip"}


# ---- signature
def test_signature_is_order_independent_and_distinguishes_sets():
    a = compute_hash(["keycloak:public", "keycloak:cskh"])
    assert a == compute_hash(["keycloak:cskh", "keycloak:public"])
    assert a != compute_hash(["keycloak:public"])


# ---- prompts
def test_prompt_render_and_missing_variable():
    sysm, user = prompts.render("rag_answer", question="Q?", context="C", history="-", no_answer="X")
    assert "Q?" in user and "X" in sysm
    with pytest.raises(prompts.PromptError):
        prompts.render("rag_answer", question="Q?")


def test_prompt_version_stable():
    assert prompts.version("rag_answer") == prompts.version("rag_answer")


# ---- canary audit
def test_canary_detection():
    found = {c["id"] for c in audit.find("Khách VIP được đổi trả trong 33 ngày, tối đa 47 ngày")}
    assert {"vip_33", "vip_47"} <= found
    assert audit.find("Khách hàng được đổi trả trong 7 ngày") == []
    assert {c["id"] for c in audit.find("chiết khấu 12,5%")} == {"n_c1"}


# ---- keycloak event dedupe (Keycloak 26.0 không có id)
def test_event_key_without_id():
    e1 = {"time": 1, "operationType": "DELETE", "resourceType": "REALM_ROLE_MAPPING", "resourcePath": "users/a"}
    e2 = dict(e1, resourcePath="users/b")
    assert _event_key(e1) != _event_key(e2)
