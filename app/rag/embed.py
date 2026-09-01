"""Local embeddings. Nothing leaves the machine, and the model is small enough to be fast."""

from __future__ import annotations

import functools
import threading

import numpy as np

# The corpus is Dutch (arbeidsreglement, opleidingsplan, kilometervergoeding) and English
# (CVs, AI policy) in one index, and a Dutch question has to reach an English CV. An
# English-only model would fail every question for the wrong reason.
MODEL_NAME = "intfloat/multilingual-e5-small"
# e5 requires these prefixes and is measurably worse without them. Asymmetric on
# purpose: a question and the passage answering it are different kinds of text.
QUERY_PREFIX = "query: "
PASSAGE_PREFIX = "passage: "


# The server warms the models on a background thread while it is already serving, so
# a question asked during the warm-up would otherwise load a second copy: lru_cache
# does not hold a lock across the call it is caching.
_loading = threading.Lock()


def _model():
    with _loading:
        return _load()


@functools.lru_cache(maxsize=1)
def _load():
    from sentence_transformers import SentenceTransformer

    return SentenceTransformer(MODEL_NAME)


def embed_passages(texts: list[str]) -> np.ndarray:
    return _model().encode(
        [PASSAGE_PREFIX + t for t in texts],
        normalize_embeddings=True,
        show_progress_bar=True,
    ).astype(np.float32)


def embed_query(text: str) -> np.ndarray:
    return _model().encode(
        [QUERY_PREFIX + text], normalize_embeddings=True
    ).astype(np.float32)[0]
