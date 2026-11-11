"""Chunking theo cấu trúc Markdown (plan mục 5.3).

1. Tách theo tiêu đề -> mỗi mục là đơn vị cơ sở.
2. Mục <= max_tokens: giữ nguyên. Mục dài: tách theo đoạn/dòng, overlap.
3. Mục quá ngắn: gộp với mục kế tiếp CÙNG mục cha.
4. Bảng: tách theo nhóm dòng, lặp lại dòng tiêu đề.
5. Thêm header path "Tiêu đề tài liệu > Mục > Mục con" vào đầu nội dung đem embed.
6. Chunk KHÔNG BAO GIỜ vượt ranh giới tài liệu; chunk_id gồm doc_id + version.
"""
from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from functools import lru_cache

import tiktoken

_HEADING = re.compile(r"^(#{1,6})\s+(.*)$")


@lru_cache
def _enc():
    return tiktoken.get_encoding("cl100k_base")


def ntokens(text: str) -> int:
    return len(_enc().encode(text))


@dataclass
class Chunk:
    chunk_id: str
    doc_id: str
    version: int
    collection: str
    title: str
    section_path: str
    text: str            # nội dung gốc của đoạn
    embed_text: str      # header path + nội dung (đem embed)
    index: int


@dataclass
class _Section:
    path: list[str]
    lines: list[str]

    @property
    def body(self) -> str:
        return "\n".join(self.lines).strip()


def _sections(md: str, title: str) -> list[_Section]:
    out: list[_Section] = []
    stack: list[tuple[int, str]] = []
    cur = _Section([title], [])
    for line in md.splitlines():
        m = _HEADING.match(line)
        if m:
            if cur.body:
                out.append(cur)
            level, name = len(m.group(1)), m.group(2).strip()
            if level == 1:          # H1 = tiêu đề tài liệu
                stack = []
                cur = _Section([title], [])
                continue
            stack = [s for s in stack if s[0] < level] + [(level, name)]
            cur = _Section([title] + [s[1] for s in stack], [])
        else:
            cur.lines.append(line)
    if cur.body:
        out.append(cur)
    return out


def _split_long(body: str, max_tokens: int, overlap: int) -> list[str]:
    lines = [ln for ln in body.splitlines()]
    is_table = sum(ln.strip().startswith("|") for ln in lines) >= max(2, len([x for x in lines if x.strip()]) // 2)
    if is_table:
        header = [ln for ln in lines[:2] if ln.strip().startswith("|")]
        rows = [ln for ln in lines[len(header):]]
        parts, buf = [], []
        for row in rows:
            if buf and ntokens("\n".join(header + buf + [row])) > max_tokens:
                parts.append("\n".join(header + buf))
                buf = []
            buf.append(row)
        if buf:
            parts.append("\n".join(header + buf))
        return parts
    units = [u for u in re.split(r"\n\s*\n|\n(?=\s*[-*\d]+[.)]?\s)", body) if u.strip()]
    parts, buf = [], ""
    for u in units:
        cand = (buf + "\n" + u).strip()
        if buf and ntokens(cand) > max_tokens:
            parts.append(buf)
            tail = _enc().decode(_enc().encode(buf)[-overlap:]) if overlap else ""
            buf = (tail + "\n" + u).strip()
        else:
            buf = cand
    if buf:
        parts.append(buf)
    return parts


def chunk_document(doc_id: str, version: int, collection: str, title: str, md: str,
                   max_tokens: int = 400, min_tokens: int = 80, overlap: int = 50) -> list[Chunk]:
    secs = _sections(md, title)
    # gộp mục quá ngắn với mục kế tiếp cùng mục cha
    merged: list[_Section] = []
    for s in secs:
        prev = merged[-1] if merged else None
        if (prev and ntokens(prev.body) < min_tokens and prev.path[:-1] == s.path[:-1]
                and ntokens(prev.body + s.body) <= max_tokens):
            prev.lines += ["", f"**{s.path[-1]}**"] + s.lines
            continue
        merged.append(_Section(list(s.path), list(s.lines)))

    chunks: list[Chunk] = []
    for s in merged:
        pieces = [s.body] if ntokens(s.body) <= max_tokens else _split_long(s.body, max_tokens, overlap)
        path = " > ".join(s.path)
        for p in pieces:
            idx = len(chunks)
            cid = hashlib.sha1(f"{doc_id}|{version}|{path}|{idx}".encode()).hexdigest()[:16]
            chunks.append(Chunk(cid, doc_id, version, collection, title, path, p, f"[{path}]\n{p}", idx))
    return chunks
