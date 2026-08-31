import numpy as np

from rag.index import Bm25Index, DenseIndex
from rag.models import Config, Chunk
from rag.pipeline import Engine


class StubLLM:
    def __init__(self) -> None:
        self.prompts: list[str] = []

    def complete(self, system: str, prompt: str, **kwargs) -> str:
        self.prompts.append(prompt)
        return "rewritten query" if "Question:" in prompt and "Sources:" not in prompt else "An answer [1]."


class WordCountReranker:
    def score(self, query: str, texts: list[str]) -> list[float]:
        return [float(len(t.split())) for t in texts]


def _chunk(cid: str, text: str) -> Chunk:
    return Chunk(id=cid, text=text, source="s", source_type="cv", title=cid, location="l")


def _engine(llm=None):
    chunks = [
        _chunk("a", "AZ-104 and AZ-400 azure administration"),
        _chunk("b", "AZ-204 developing solutions for microsoft azure"),
        _chunk("c", "kubernetes platform engineering with many many many words here"),
    ]
    vectors = np.array([[1.0, 0.0], [0.9, 0.436], [0.0, 1.0]], dtype=np.float32)
    return Engine(
        dense=DenseIndex(chunks, vectors),
        bm25=Bm25Index(chunks),
        reranker=WordCountReranker(),
        llm=llm or StubLLM(),
        embed_query=lambda _: np.array([1.0, 0.0], dtype=np.float32),
    )


def test_dense_only_never_consults_bm25():
    result = _engine().run("AZ-204", Config(top_n=2))
    assert all("bm25" not in s.ranks for s in result.candidates)


def test_hybrid_records_both_retrievers():
    result = _engine().run("AZ-204", Config(bm25=True, top_n=3))
    assert any("bm25" in s.ranks for s in result.candidates)


def test_rerank_populates_the_rerank_rank():
    result = _engine().run("kubernetes", Config(bm25=True, rerank=True, top_n=2))
    assert all("rerank" in s.ranks for s in result.used)


def test_used_is_capped_at_top_n():
    result = _engine().run("azure", Config(bm25=True, top_n=2))
    assert len(result.used) == 2


def test_rewrite_off_leaves_rewritten_none():
    assert _engine().run("AZ-204", Config()).rewritten is None


def test_rewrite_on_sets_rewritten_and_searches_with_it():
    result = _engine().run("AZ-204", Config(rewrite=True, top_n=2))
    assert result.rewritten == "rewritten query"


def test_aggregate_chunks_are_hidden_until_enabled():
    chunks = [
        _chunk("a", "AZ-104 and AZ-400 azure administration"),
        Chunk(id="agg", text="Current balance: 340 credits", source="s",
              source_type="aggregate", title="Dries", location="summary"),
    ]
    vectors = np.array([[1.0, 0.0], [1.0, 0.0]], dtype=np.float32)
    engine = Engine(
        dense=DenseIndex(chunks, vectors),
        bm25=Bm25Index(chunks),
        reranker=WordCountReranker(),
        llm=StubLLM(),
        embed_query=lambda _: np.array([1.0, 0.0], dtype=np.float32),
    )
    hidden = engine.run("credits", Config(top_n=5))
    assert all(s.chunk.source_type != "aggregate" for s in hidden.used)
    shown = engine.run("credits", Config(aggregates=True, top_n=5))
    assert any(s.chunk.source_type == "aggregate" for s in shown.used)


def test_citations_only_extracted_when_enabled():
    assert _engine().run("azure", Config(top_n=2)).citations == []
    with_citations = _engine().run("azure", Config(citations=True, top_n=2))
    assert with_citations.citations[0].marker == 1


def test_retrieval_survives_a_generation_failure():
    """On stage, an unreachable model must not take the retrieved chunks down with it."""

    class Broken:
        def complete(self, system, prompt, **kwargs):
            raise RuntimeError("credit balance is too low")

    result = _engine(Broken()).run("azure", Config(bm25=True, top_n=2))
    assert len(result.used) == 2
    assert "credit balance is too low" in result.answer
    assert result.citations == []
