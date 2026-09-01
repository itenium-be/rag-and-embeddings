from rag.fuse import reciprocal_rank_fusion
from rag.models import Chunk


def _chunk(cid: str) -> Chunk:
    return Chunk(id=cid, text=cid, source="s", source_type="cv", title=cid, location="l")


A, B, C = _chunk("a"), _chunk("b"), _chunk("c")


def test_chunk_found_by_both_retrievers_beats_one_found_by_one():
    fused = reciprocal_rank_fusion({"dense": [A, B], "bm25": [B]})
    assert [s.chunk.id for s in fused] == ["b", "a"]


def test_first_and_third_beats_second_and_second():
    # RRF is convex in rank: 1/(k+1) + 1/(k+3) > 2/(k+2). A chunk one retriever loves
    # and the other dislikes outranks one that both merely tolerate. Surprising, and
    # the reason RRF does not just average ranks.
    fused = reciprocal_rank_fusion({"dense": [A, B, C], "bm25": [C, B, A]})
    assert fused[-1].chunk.id == "b"


def test_ranks_record_the_position_in_each_retriever():
    fused = reciprocal_rank_fusion({"dense": [A, B], "bm25": [B, A]})
    by_id = {s.chunk.id: s for s in fused}
    assert by_id["a"].ranks["dense"] == 1 and by_id["a"].ranks["bm25"] == 2
    assert by_id["b"].ranks["dense"] == 2 and by_id["b"].ranks["bm25"] == 1


def test_ranks_record_the_merged_position():
    # Without this the projector cannot show what reranking did: a chunk fused at 39
    # and reranked to 3 is the whole argument for the technique, and comparing against
    # a single retriever's rank understates it.
    fused = reciprocal_rank_fusion({"dense": [A, B, C], "bm25": [C, B, A]})
    assert [s.ranks["fused"] for s in fused] == [1, 2, 3]


def test_chunk_found_by_one_retriever_only_still_appears():
    fused = reciprocal_rank_fusion({"dense": [A], "bm25": [B]})
    assert {s.chunk.id for s in fused} == {"a", "b"}
    assert all(len(s.ranks) == 2 for s in fused)  # its retriever, plus "fused"


def test_single_retriever_preserves_its_order():
    fused = reciprocal_rank_fusion({"dense": [A, B, C]})
    assert [s.chunk.id for s in fused] == ["a", "b", "c"]


def test_scores_descend():
    fused = reciprocal_rank_fusion({"dense": [A, B, C], "bm25": [C, B, A]})
    scores = [s.score for s in fused]
    assert scores == sorted(scores, reverse=True)
