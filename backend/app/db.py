"""Postgres: tài liệu, session chat, trace, sự kiện bảo mật."""
from __future__ import annotations

from contextlib import contextmanager
from functools import lru_cache

from psycopg.rows import dict_row
from psycopg.types.json import Jsonb
from psycopg_pool import ConnectionPool

from .config import env

SCHEMA = """
CREATE TABLE IF NOT EXISTS documents (
    doc_id      TEXT PRIMARY KEY,
    title       TEXT NOT NULL,
    collection  TEXT NOT NULL,
    version     INT  NOT NULL,
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE TABLE IF NOT EXISTS sessions (
    id          UUID PRIMARY KEY,
    user_id     TEXT NOT NULL,
    username    TEXT NOT NULL,
    title       TEXT NOT NULL,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS sessions_user ON sessions(user_id, updated_at DESC);
CREATE TABLE IF NOT EXISTS messages (
    id          UUID PRIMARY KEY,
    session_id  UUID NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    role        TEXT NOT NULL,
    content     TEXT NOT NULL,
    trace_id    UUID,
    cache_status TEXT,
    citations   JSONB,
    feedback    SMALLINT,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS messages_session ON messages(session_id, created_at);
CREATE TABLE IF NOT EXISTS traces (
    id            UUID PRIMARY KEY,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    user_id       TEXT NOT NULL,
    username      TEXT NOT NULL,
    session_id    UUID,
    question      TEXT NOT NULL,
    status        TEXT NOT NULL,
    policy        TEXT,
    intent        TEXT,
    partition     TEXT,
    similarity    DOUBLE PRECISION,
    entry_id      TEXT,
    latency_ms    DOUBLE PRECISION,
    llm_tokens_in  INT DEFAULT 0,
    llm_tokens_out INT DEFAULT 0,
    embed_tokens   INT DEFAULT 0,
    cost_usd       DOUBLE PRECISION DEFAULT 0,
    saved_tokens   INT DEFAULT 0,
    saved_cost_usd DOUBLE PRECISION DEFAULT 0,
    audit          JSONB,
    unauthorized   BOOLEAN,
    feedback       SMALLINT,
    spans          JSONB NOT NULL
);
CREATE INDEX IF NOT EXISTS traces_created ON traces(created_at DESC);
CREATE TABLE IF NOT EXISTS security_events (
    id           BIGSERIAL PRIMARY KEY,
    kind         TEXT NOT NULL,
    source       TEXT NOT NULL,
    occurred_at  TIMESTAMPTZ NOT NULL,
    detected_at  TIMESTAMPTZ NOT NULL,
    effective_at TIMESTAMPTZ,
    summary      TEXT NOT NULL,
    details      JSONB
);
CREATE INDEX IF NOT EXISTS security_events_time ON security_events(occurred_at DESC);
"""


@lru_cache
def pool() -> ConnectionPool:
    p = ConnectionPool(env().postgres_dsn, min_size=1, max_size=10, kwargs={"row_factory": dict_row}, open=True)
    return p


@contextmanager
def conn():
    with pool().connection() as c:
        yield c


def init_schema() -> None:
    with conn() as c:
        c.execute(SCHEMA)


def fetch_all(sql: str, params: tuple | dict = ()) -> list[dict]:
    with conn() as c:
        return list(c.execute(sql, params).fetchall())


def fetch_one(sql: str, params: tuple | dict = ()) -> dict | None:
    with conn() as c:
        return c.execute(sql, params).fetchone()


def execute(sql: str, params: tuple | dict = ()) -> None:
    with conn() as c:
        c.execute(sql, params)


__all__ = ["Jsonb", "conn", "execute", "fetch_all", "fetch_one", "init_schema", "pool"]
