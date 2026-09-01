from __future__ import annotations

import functools
import threading
from typing import Protocol

from rag.models import Scored

# Multilingual, to match the embedding model.
MODEL_NAME = "BAAI/bge-reranker-v2-m3"


class Reranker(Protocol):
    def score(self, query: str, texts: list[str]) -> list[float]: ...


class CrossEncoderReranker:
    def score(self, query: str, texts: list[str]) -> list[float]:
        pairs = [(query, text) for text in texts]
        return [float(s) for s in _model().predict(pairs)]


# The server warms the models on a background thread while it is already serving, so
# a question asked during the warm-up would otherwise load a second copy: lru_cache
# does not hold a lock across the call it is caching.
_loading = threading.Lock()


def _model():
    with _loading:
        return _load()


@functools.lru_cache(maxsize=1)
def _load():
    from sentence_transformers import CrossEncoder

    return CrossEncoder(MODEL_NAME)


def apply_rerank(
    reranker: Reranker, query: str, candidates: list[Scored], *, top_n: int
) -> list[Scored]:
    if not candidates:
        return []
    scores = reranker.score(query, [c.chunk.text for c in candidates])
    ordered = sorted(zip(candidates, scores), key=lambda pair: -pair[1])
    return [
        Scored(candidate.chunk, score, {**candidate.ranks, "rerank": position})
        for position, (candidate, score) in enumerate(ordered[:top_n], start=1)
    ]
