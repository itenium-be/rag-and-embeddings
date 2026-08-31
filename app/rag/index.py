from __future__ import annotations

import re

import numpy as np
from rank_bm25 import BM25Okapi

from rag.models import Chunk

# Hyphens and dots stay inside a token so `az-204` survives as one term. Splitting it
# into `az` + `204` would let AZ-104 match half the query, which is the failure hybrid
# search is supposed to fix.
TOKEN = re.compile(r"[a-z0-9][a-z0-9._-]*")

# Without these, BM25 is useless on this corpus. Function words score positively —
# rank_bm25 floors negative idf to a small positive epsilon — and the long Dutch
# documents accumulate enough of them to bury an exact rare term, so "Wie heeft DP-600?"
# returns the arbeidsreglement. A frequency threshold does not find them either: the
# corpus is half CVs and ledger rows, which contain no Dutch prose at all, so "wie" and
# "heeft" sit below any sane document-frequency cutoff.
STOPWORDS = frozenset("""
ik jij hij zij wij het de een en van is dat die te in op voor met als aan er om ook bij
maar dan heeft hebben heb zijn was worden wordt mijn je ze niet naar uit over al wil moet
moeten kan kunnen mag mogen wie wat waar hoe wanneer waarom welke welk dit deze hun ons
onze uw men zich meer nog wel geen door tot na onder boven tussen per
the a an of to in for with is are was be and or my i you it this that
""".split())


def tokenize(text: str) -> list[str]:
    return TOKEN.findall(text.lower())


def query_terms(query: str) -> list[str]:
    return [t for t in tokenize(query) if t not in STOPWORDS]


class DenseIndex:
    """Brute-force cosine similarity. A few thousand vectors is a millisecond."""

    def __init__(self, chunks: list[Chunk], vectors: np.ndarray) -> None:
        if len(chunks) != len(vectors):
            raise ValueError(f"{len(chunks)} chunks but {len(vectors)} vectors")
        self.chunks = chunks
        self.vectors = vectors.astype(np.float32)

    def search(self, query_vector: np.ndarray, k: int) -> list[tuple[Chunk, float]]:
        scores = self.vectors @ query_vector.astype(np.float32)
        top = np.argsort(-scores)[:k]
        return [(self.chunks[i], float(scores[i])) for i in top]


class Bm25Index:
    def __init__(self, chunks: list[Chunk]) -> None:
        self.chunks = chunks
        self._tokens = [set(tokenize(c.text)) for c in chunks]
        self._bm25 = BM25Okapi([tokenize(c.text) for c in chunks])

    def search(self, query: str, k: int) -> list[tuple[Chunk, float]]:
        tokens = query_terms(query)
        if not tokens:
            return []
        scores = self._bm25.get_scores(tokens)
        top = np.argsort(-scores)[:k]
        # Discarding on `score > 0` would be wrong. rank_bm25 computes
        # idf = log(N - f + 0.5) - log(f + 0.5), which is exactly zero for a term in
        # half the corpus, so a real match can score 0.0 and become indistinguishable
        # from no match at all. Whether the chunk contains a query term is the actual
        # question, and it is the one worth asking.
        wanted = set(tokens)
        return [
            (self.chunks[i], float(scores[i])) for i in top if wanted & self._tokens[i]
        ]
