"""Local embeddings. Nothing leaves the machine, and the model is small enough to be fast."""

from __future__ import annotations

import functools

import numpy as np

# The corpus is Dutch (arbeidsreglement, opleidingsplan, kilometervergoeding) and English
# (CVs, AI policy) in one index, and a Dutch question has to reach an English CV. An
# English-only model would fail every question for the wrong reason.
MODEL_NAME = "intfloat/multilingual-e5-small"
# e5 requires these prefixes and is measurably worse without them. Asymmetric on
# purpose: a question and the passage answering it are different kinds of text.
QUERY_PREFIX = "query: "
PASSAGE_PREFIX = "passage: "


@functools.lru_cache(maxsize=1)
def _model():
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
