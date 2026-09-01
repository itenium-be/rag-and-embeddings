from __future__ import annotations

import pytest

from rag.longcontext import SYSTEM, build_corpus, answer
from rag.models import Chunk


def chunk(id, title, source, location, text, source_type="policy"):
    return Chunk(
        id=id, text=text, source=source, source_type=source_type, title=title, location=location
    )


class FakeLLM:
    def __init__(self, response="answered"):
        self.response = response
        self.calls = []

    def complete(self, system, prompt, **kwargs):
        self.calls.append((system, prompt, kwargs))
        return self.response


def test_build_corpus_numbers_every_chunk():
    corpus = build_corpus(
        [
            chunk("a", "AI Policy", "ai.pdf", "AI Policy > p. 1", "eerste"),
            chunk("b", "AI Policy", "ai.pdf", "AI Policy > p. 2", "tweede"),
        ]
    )
    assert "[1] AI Policy — AI Policy > p. 1\neerste" in corpus
    assert "[2] AI Policy — AI Policy > p. 2\ntweede" in corpus


def test_build_corpus_drops_aggregate_chunks():
    corpus = build_corpus(
        [
            chunk("a", "Ledger", "credits.json", "Ledger > 2025", "boeking", "credit"),
            chunk("b", "Saldo", "credits.json", "Saldo", "Huidig saldo 1894", "aggregate"),
        ]
    )
    assert "boeking" in corpus
    assert "Huidig saldo" not in corpus


def test_build_corpus_keeps_each_document_contiguous():
    """A document split over several chunks has to read as one document, not as shuffled
    pages: whatever order the index happens to be in, the prompt is the corpus."""
    corpus = build_corpus(
        [
            chunk("a1", "AI Policy", "ai.pdf", "AI Policy > p. 1", "alpha"),
            chunk("b1", "Laptop policy", "laptop.pdf", "Laptop policy > p. 1", "beta"),
            chunk("a2", "AI Policy", "ai.pdf", "AI Policy > p. 2", "gamma"),
        ]
    )
    assert corpus.index("alpha") < corpus.index("gamma") < corpus.index("beta")


def test_build_corpus_sorts_pages_numerically():
    """`p. 10` sorts after `p. 9`, which a plain string sort gets wrong."""
    corpus = build_corpus(
        [
            chunk("a", "Policy", "p.pdf", "Policy > p. 10", "tenth"),
            chunk("b", "Policy", "p.pdf", "Policy > p. 9", "ninth"),
        ]
    )
    assert corpus.index("ninth") < corpus.index("tenth")


def test_answer_puts_the_question_after_the_corpus():
    """The corpus is the cacheable prefix, so it goes first and the question last."""
    llm = FakeLLM()
    answer(llm, "Hoeveel credits?", "[1] Ledger — Ledger\nboeking")
    _, prompt, _ = llm.calls[0]
    assert prompt.index("boeking") < prompt.index("Hoeveel credits?")


def test_answer_passes_the_question_as_its_own_fallback():
    llm = FakeLLM()
    answer(llm, "Hoeveel credits?", "corpus")
    assert llm.calls[0][2]["fallback_to"] == "Hoeveel credits?"


def test_answer_uses_the_shared_system_prompt():
    """Same instructions as generation, so the only difference from RAG is what it sees."""
    llm = FakeLLM()
    answer(llm, "vraag", "corpus")
    assert llm.calls[0][0] == SYSTEM


def test_answer_strips_the_response():
    assert answer(FakeLLM("  antwoord  "), "vraag", "corpus") == "antwoord"


def test_build_corpus_refuses_an_empty_corpus():
    with pytest.raises(ValueError):
        build_corpus([chunk("a", "Saldo", "c.json", "Saldo", "x", "aggregate")])
