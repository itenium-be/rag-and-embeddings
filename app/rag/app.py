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
REAL_INDEX_DIR = APP_DIR / "data" / "index-real"
CACHE_DIR = APP_DIR / "data" / "cache"


def default_index_dir() -> Path:
    """The real corpus when it has been built, the committed sample otherwise.

    Everything that reads an index goes through here, so the server, the cache warmer
    and the scoreboard can never end up pointed at different corpora.
    """
    return REAL_INDEX_DIR if REAL_INDEX_DIR.is_dir() else INDEX_DIR


def build_engine(index_dir: Path | None = None, cache_dir: Path = CACHE_DIR) -> Engine:
    index_dir = index_dir or default_index_dir()
    chunks, vectors, _ = load_artefacts(index_dir)
    return Engine(
        dense=DenseIndex(chunks, vectors),
        bm25=Bm25Index(chunks),
        reranker=CrossEncoderReranker(),
        llm=build_llm(cache_dir),
        embed_query=embed_query,
    )


def load_projection(index_dir: Path | None = None):
    index_dir = index_dir or default_index_dir()
    chunks, _, projection = load_artefacts(index_dir)
    return chunks, projection
