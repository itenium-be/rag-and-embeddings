"""The whole pipeline. This is the module that goes on a slide — keep it readable."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import numpy as np

from rag.fuse import reciprocal_rank_fusion
from rag.generate import extract_citations, generate_answer
from rag.index import Bm25Index, DenseIndex
from rag.models import Chunk, Config, Result, Scored
from rag.rerank import Reranker, apply_rerank
from rag.rewrite import rewrite_query


@dataclass
class Engine:
    dense: DenseIndex
    bm25: Bm25Index
    reranker: Reranker
    llm: object
    embed_query: Callable[[str], np.ndarray]

    def retrieve(self, query: str, config: Config) -> list[Scored]:
        def visible(hits) -> list[Chunk]:
            return [
                chunk
                for chunk, _ in hits
                if config.aggregates or chunk.source_type != "aggregate"
            ]

        rankings: dict[str, list[Chunk]] = {}
        if config.dense:
            rankings["dense"] = visible(self.dense.search(self.embed_query(query), config.top_k))
        if config.bm25:
            rankings["bm25"] = visible(self.bm25.search(query, config.top_k))
        return reciprocal_rank_fusion(rankings)

    def run(self, question: str, config: Config) -> Result:
        query = question
        rewritten = None
        if config.rewrite:
            rewritten = rewrite_query(self.llm, question)
            query = rewritten

        candidates = self.retrieve(query, config)

        if config.rerank:
            used = apply_rerank(self.reranker, query, candidates, top_n=config.top_n)
        else:
            used = candidates[: config.top_n]

        answer = generate_answer(self.llm, question, used, fallback_to=question)
        citations = extract_citations(answer, used) if config.citations else []

        return Result(
            question=question,
            rewritten=rewritten,
            candidates=candidates,
            used=used,
            answer=answer,
            citations=citations,
        )
