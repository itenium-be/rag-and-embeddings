from rag.fuse import reciprocal_rank_fusion
from rag.generate import extract_citations, generate_answer
from rag.models import Chunk
from rag.rewrite import rewrite_query


class ScriptedLLM:
    def __init__(self, reply: str) -> None:
        self.reply = reply
        self.last_prompt = ""

    def complete(self, system: str, prompt: str, **kwargs) -> str:
        self.last_prompt = prompt
        return self.reply


def _chunk(cid: str, text: str) -> Chunk:
    return Chunk(id=cid, text=text, source="s", source_type="cv", title=cid, location="Section")


def test_rewrite_returns_the_broadened_question():
    llm = ScriptedLLM("Which consultants are available and what does ACME need?")
    assert rewrite_query(llm, "Who can take over ACME in October?").startswith("Which")


def test_rewrite_passes_the_original_question_through():
    llm = ScriptedLLM("broadened")
    rewrite_query(llm, "Who has AZ-204?")
    assert "Who has AZ-204?" in llm.last_prompt


def test_rewrite_falls_back_to_the_original_on_an_empty_reply():
    assert rewrite_query(ScriptedLLM("  "), "original") == "original"


def test_generate_numbers_the_sources_in_the_prompt():
    llm = ScriptedLLM("The budget is EUR 2000 [1].")
    candidates = reciprocal_rank_fusion({"dense": [_chunk("a", "budget is EUR 2000")]})
    generate_answer(llm, "What is the budget?", candidates)
    assert "[1]" in llm.last_prompt
    assert "budget is EUR 2000" in llm.last_prompt


def test_extract_citations_maps_markers_to_chunks():
    candidates = reciprocal_rank_fusion(
        {"dense": [_chunk("a", "first"), _chunk("b", "second")]}
    )
    citations = extract_citations("Claim one [1]. Claim two [2].", candidates)
    assert [c.marker for c in citations] == [1, 2]
    assert [c.chunk_id for c in citations] == ["a", "b"]


def test_extract_citations_ignores_markers_with_no_source():
    candidates = reciprocal_rank_fusion({"dense": [_chunk("a", "first")]})
    assert extract_citations("Claim [7].", candidates) == []


def test_extract_citations_deduplicates():
    candidates = reciprocal_rank_fusion({"dense": [_chunk("a", "first")]})
    assert len(extract_citations("A [1]. B [1].", candidates)) == 1
