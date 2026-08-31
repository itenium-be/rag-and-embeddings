"""Assembles an Engine from artefacts on disk. Used by the server, the scripts and the tests."""

from __future__ import annotations

from pathlib import Path

from rag.embed import embed_query
from rag.index import Bm25Index, DenseIndex
from rag.llm import build_llm
from rag.pipeline import Engine
from rag.rerank import CrossEncoderReranker
from rag.store import load_artefacts

APP_DIR = Path(__file__).resolve().parents[1]
INDEX_DIR = APP_DIR / "data" / "index"
CACHE_DIR = APP_DIR / "data" / "cache"


def build_engine(index_dir: Path = INDEX_DIR, cache_dir: Path = CACHE_DIR) -> Engine:
    chunks, vectors, _ = load_artefacts(index_dir)
    return Engine(
        dense=DenseIndex(chunks, vectors),
        bm25=Bm25Index(chunks),
        reranker=CrossEncoderReranker(),
        llm=build_llm(cache_dir),
        embed_query=embed_query,
    )


def load_projection(index_dir: Path = INDEX_DIR):
    chunks, _, projection = load_artefacts(index_dir)
    return chunks, projection
