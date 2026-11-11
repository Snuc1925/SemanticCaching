"""Kết nối dùng chung: Redis, Qdrant, OpenAI, Gemini (tạo một lần)."""
from __future__ import annotations

from functools import lru_cache

import redis
from qdrant_client import QdrantClient

from .config import env


@lru_cache
def rds() -> redis.Redis:
    return redis.Redis.from_url(env().redis_url, decode_responses=True)


@lru_cache
def qdrant() -> QdrantClient:
    return QdrantClient(url=env().qdrant_url, timeout=30)


@lru_cache
def openai_client():
    from openai import OpenAI

    return OpenAI(api_key=env().openai_api_key)


@lru_cache
def gemini_client():
    from google import genai

    return genai.Client(api_key=env().gemini_api_key)
