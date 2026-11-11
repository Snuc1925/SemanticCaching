"""Luồng xử lý một câu hỏi (plan mục 4.1). Mỗi bước ghi một span vào trace để Console hiển thị."""
from __future__ import annotations

import re
import time
from dataclasses import asdict, dataclass

from . import access, cache, classifier, embeddings, llm, prompts, retrieval
from .config import settings
from .iam.base import UserContext
from .tracing import Trace

RAG_PROMPT = "rag_answer"
_CITE = re.compile(r"\[(c\d+)\]")


@dataclass
class ChatResult:
    trace_id: str
    status: str                 # HIT | MISS | BYPASS | NO_CACHE
    answer: str
    citations: list[dict]
    latency_ms: float
    policy: str
    similarity: float | None


def no_answer_text() -> str:
    return prompts.text("no_answer_text")


def _citations(answer: str, chunks: list[retrieval.Retrieved]) -> list[dict]:
    by_label = {c.label: c for c in chunks}
    out, seen = [], set()
    for label in _CITE.findall(answer):
        c = by_label.get(label)
        if c and label not in seen:
            seen.add(label)
            out.append({"label": label, "doc_id": c.doc_id, "title": c.title, "section": c.section_path,
                        "collection": c.collection, "version": c.version})
    return out


def answer(user: UserContext, question: str, session_id: str | None = None,
           history: list[dict] | None = None, tr: Trace | None = None) -> tuple[ChatResult, Trace]:
    tr = tr or Trace(user.user_id, user.username, question, session_id)
    cfg = settings()
    ad = access.adapter()

    # 1. Danh tính & access signature
    with tr.span("identity", "Danh tính & access signature") as d:
        sig = access.get(user)
        d.update(user=user.username, roles=list(user.roles), signature=sig.signature,
                 collections=sig.collections, signature_from_cache=sig.from_cache)
    tr.set(partition=sig.signature)

    # 2. Embedding câu hỏi
    with tr.span("embed", "Embedding câu hỏi") as d:
        vec, etok, ehit = embeddings.embed_one(question)
        d.update(model=embeddings.model(), tokens=etok, from_cache=ehit)
    tr.set(embed_tokens=etok)

    # 3. Phân loại
    with tr.span("classify", "Phân loại câu hỏi") as d:
        cls = classifier.classify(question, vec)
        d.update(policy=cls.policy, reason=cls.reason, intent=cls.intent,
                 intent_similarity=round(cls.intent_similarity, 3), entities=cls.entities)
    tr.set(policy=cls.policy, intent=cls.intent)
    cacheable = cfg["cache"]["enabled"] and cls.policy in ("NORMAL", "SHORT_TTL")
    prompt_version = prompts.version(RAG_PROMPT)

    # 4. Tra cache trong partition
    if cacheable:
        with tr.span("cache_lookup", "Tra cache (partition theo signature)") as d:
            reverify = None
            if cfg["cache"].get("reverify_iam_on_hit"):
                def reverify(cols):  # noqa: E306
                    return ad.check_collections(user, cols)
            lk = cache.lookup(vec, sig.signature, cls.intent, cls.entities, prompt_version, reverify)
            d.update(partition=sig.signature, threshold=cache.threshold_for(cls.intent),
                     top_similarity=lk.similarity, result="HIT" if lk.hit else "MISS",
                     candidates=[asdict(c) for c in lk.candidates])
            if lk.hit is None and any("IAM re-verify" in c.reason for c in lk.candidates):
                access.invalidate(user.user_id)      # signature đang cũ -> tính lại lần sau
                d["signature_invalidated"] = True
        if lk.hit:
            e = lk.hit
            with tr.span("cache_hit", "Trả lời từ cache") as d:
                d.update(entry_id=e.entry_id, cached_question=e.question, created_at=e.created_at,
                         hits=e.hits, provenance=[asdict(p) for p in e.provenance],
                         saved_tokens=e.gen_tokens_in + e.gen_tokens_out, saved_cost_usd=e.gen_cost_usd)
            lat = tr.elapsed_ms()
            tr.set(status="HIT", similarity=lk.similarity, entry_id=e.entry_id, latency_ms=lat,
                   cost_usd=llm.cost_usd(0, 0, etok), saved_tokens=e.gen_tokens_in + e.gen_tokens_out,
                   saved_cost_usd=e.gen_cost_usd)
            return ChatResult(tr.id, "HIT", e.answer, e.citations, lat, cls.policy, lk.similarity), tr
        tr.set(similarity=lk.similarity)

    # 5. Retrieval với pre-filter theo collection của signature
    with tr.span("retrieval", "Retrieval (pre-filter theo quyền)") as d:
        chunks = retrieval.search(vec, sig.collections)
        d.update(filter_collections=sig.collections, top_k=cfg["retrieval"]["top_k"],
                 chunks=[{"chunk_id": c.chunk_id, "doc_id": c.doc_id, "version": c.version,
                          "collection": c.collection, "section": c.section_path, "score": round(c.score, 3),
                          "preview": c.text[:160]} for c in chunks])

    # 6. IAM post-verify (trọng tài cuối, giống PermRAG)
    with tr.span("iam_verify", "IAM kiểm tra lại (post-verify)") as d:
        cols = {c.collection for c in chunks}
        decisions = ad.check_collections(user, cols) if cols else {}
        allowed = [c for c in chunks if decisions.get(c.collection, False)]
        blocked = [c for c in chunks if not decisions.get(c.collection, False)]
        d.update(decisions=decisions, allowed=len(allowed),
                 blocked=[{"chunk_id": c.chunk_id, "collection": c.collection} for c in blocked])
        if blocked:
            access.invalidate(user.user_id)
            d["signature_invalidated"] = True

    # 7. Sinh câu trả lời
    hist_text = "(không có)"
    if cls.policy == "BYPASS" and history:
        hist_text = "\n".join(f"{m['role']}: {m['content']}" for m in history[-4:])
    if not allowed:
        ans = no_answer_text()
        res = llm.LLMResult(ans, 0, 0, 0.0, llm.model(), prompt_version)
        with tr.span("llm", "LLM (bỏ qua: không có ngữ cảnh)") as d:
            d.update(skipped=True, reason="không có đoạn tài liệu hợp lệ")
    else:
        with tr.span("llm", "LLM sinh câu trả lời") as d:
            ctx = retrieval.format_context(allowed)
            res = llm.generate(RAG_PROMPT, question=question, context=ctx, history=hist_text,
                               no_answer=no_answer_text())
            d.update(model=res.model, prompt_version=res.prompt_version, tokens_in=res.tokens_in,
                     tokens_out=res.tokens_out, latency_ms=round(res.latency_ms, 1),
                     cost_usd=llm.cost_usd(res.tokens_in, res.tokens_out))
        ans = res.text
    cites = _citations(ans, allowed)
    cost = llm.cost_usd(res.tokens_in, res.tokens_out, etok)

    # 8. Admission: có lưu vào cache không
    status = "MISS" if cacheable else cls.policy
    with tr.span("admission", "Quyết định lưu cache") as d:
        reasons = []
        if not cacheable:
            reasons.append(f"chính sách {cls.policy}: {cls.reason}")
        if not allowed:
            reasons.append("không có ngữ cảnh")
        if no_answer_text() in ans:
            reasons.append("câu trả lời 'không tìm thấy' (không cache để tránh chặn thông tin bổ sung sau này)")
        if allowed and not cites:
            reasons.append("không có trích dẫn hợp lệ -> không truy được provenance")
        d["admitted"] = not reasons
        d["reasons"] = reasons or ["đủ điều kiện"]
        if not reasons:
            ttl = cfg["cache"]["ttl_seconds"][cls.policy]
            e = cache.CacheEntry(
                entry_id=cache.new_entry_id(), partition=sig.signature, question=question, answer=ans,
                citations=cites, provenance=[cache.Provenance(c.chunk_id, c.doc_id, c.version, c.collection,
                                                              c.title, c.section_path) for c in allowed],
                intent=cls.intent, entities=cls.entities, policy=cls.policy, prompt_version=res.prompt_version,
                model=res.model, created_at=time.time(), ttl=ttl, gen_tokens_in=res.tokens_in,
                gen_tokens_out=res.tokens_out, gen_cost_usd=llm.cost_usd(res.tokens_in, res.tokens_out),
                gen_latency_ms=res.latency_ms)
            cache.store(e, vec)
            d.update(entry_id=e.entry_id, ttl=ttl, provenance_docs=sorted({p.doc_id for p in e.provenance}))
            tr.set(entry_id=e.entry_id)

    lat = tr.elapsed_ms()
    tr.set(status=status, latency_ms=lat, llm_tokens_in=res.tokens_in, llm_tokens_out=res.tokens_out, cost_usd=cost)
    return ChatResult(tr.id, status, ans, cites, lat, cls.policy, tr.fields.get("similarity")), tr
