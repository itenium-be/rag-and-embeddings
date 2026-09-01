"""Reciprocal rank fusion — the ten-line merge that surprises people."""

from __future__ import annotations

from rag.models import Chunk, Scored

# The constant damps the influence of top ranks so one retriever cannot dominate;
# 60 is the value from the original RRF paper and nobody has found better.
RRF_K = 60


def reciprocal_rank_fusion(
    rankings: dict[str, list[Chunk]], *, k: int = RRF_K
) -> list[Scored]:
    scores: dict[str, float] = {}
    ranks: dict[str, dict[str, int]] = {}
    chunks: dict[str, Chunk] = {}

    for retriever, ranked in rankings.items():
        for position, chunk in enumerate(ranked, start=1):
            chunks[chunk.id] = chunk
            scores[chunk.id] = scores.get(chunk.id, 0.0) + 1.0 / (k + position)
            ranks.setdefault(chunk.id, {})[retriever] = position

    ordered = sorted(scores, key=lambda cid: -scores[cid])
    return [
        Scored(chunks[cid], scores[cid], {**ranks[cid], "fused": position})
        for position, cid in enumerate(ordered, start=1)
    ]
