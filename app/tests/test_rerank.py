from rag.fuse import reciprocal_rank_fusion
from rag.models import Chunk
from rag.rerank import apply_rerank


class FakeReranker:
    """Scores by how many times the query word appears — enough to prove reordering."""

    def score(self, query: str, texts: list[str]) -> list[float]:
        return [float(t.lower().count(query.lower())) for t in texts]


def _chunk(cid: str, text: str) -> Chunk:
    return Chunk(id=cid, text=text, source="s", source_type="cv", title=cid, location="l")


def test_rerank_reorders_and_truncates():
    candidates = reciprocal_rank_fusion(
        {"dense": [_chunk("a", "x"), _chunk("b", "x x x"), _chunk("c", "x x")]}
    )
    top = apply_rerank(FakeReranker(), "x", candidates, top_n=2)
    assert [s.chunk.id for s in top] == ["b", "c"]


def test_rerank_records_both_ranks():
    candidates = reciprocal_rank_fusion(
        {"dense": [_chunk("a", "x"), _chunk("b", "x x x")]}
    )
    top = apply_rerank(FakeReranker(), "x", candidates, top_n=2)
    # b was second out of retrieval and first after reranking — this delta is the demo.
    assert top[0].ranks["dense"] == 2
    assert top[0].ranks["rerank"] == 1
