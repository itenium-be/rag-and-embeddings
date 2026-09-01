"""`POST /api/context`: step -1, the whole corpus and no retrieval."""

from __future__ import annotations

import numpy as np
import pytest
from fastapi.testclient import TestClient

from rag.index import Bm25Index, DenseIndex
from rag.llm import NoAnswerAvailable
from rag.models import Chunk
from rag.pipeline import Engine
from web.server import create_app

CHUNKS = [
    Chunk(id="a", text="AZ-900 behaald", source="cv.pdf", source_type="cv", title="Igor", location="cv.pdf > p. 1"),
    Chunk(id="b", text="kubernetes", source="cv2.pdf", source_type="cv", title="Dries", location="cv2.pdf > p. 1"),
    Chunk(id="c", text="Huidig saldo 1894", source="c.json", source_type="aggregate", title="Saldo", location="Saldo"),
]


class StubLLM:
    def __init__(self, usage=None):
        self.usage = usage if usage is not None else {"input_tokens": 262_000, "cost_usd": 1.31}
        self.prompts = []

    def complete(self, system, prompt, **kwargs):
        return self.complete_with_usage(system, prompt, **kwargs)[0]

    def complete_with_usage(self, system, prompt, **kwargs):
        self.prompts.append((kwargs.get("label"), prompt))
        label = kwargs.get("label")
        if label == "checklist":
            return "1. Igor genoemd", {}
        if label == "critic":
            return "1 PASS", {}
        return "Igor heeft AZ-900 [1].", self.usage


class NullReranker:
    def score(self, query, texts):
        return [0.0] * len(texts)


def build_client(llm):
    engine = Engine(
        dense=DenseIndex(CHUNKS, np.eye(3, 2, dtype=np.float32)),
        bm25=Bm25Index(CHUNKS),
        reranker=NullReranker(),
        llm=llm,
        embed_query=lambda _: np.array([1.0, 0.0], dtype=np.float32),
    )
    return TestClient(create_app(engine, CHUNKS, np.zeros((3, 2), dtype=np.float32)))


@pytest.fixture
def llm():
    return StubLLM()


@pytest.fixture
def client(llm):
    return build_client(llm)


def test_it_answers_from_the_whole_corpus(client):
    body = client.post("/api/context", json={"question": "Wie heeft AZ-900?"}).json()
    assert body["answer"] == "Igor heeft AZ-900 [1]."


def test_the_prompt_holds_every_retrievable_chunk(client, llm):
    client.post("/api/context", json={"question": "Wie heeft AZ-900?"})
    _, prompt = next((c for c in llm.prompts if c[0] == "longcontext"), (None, ""))
    assert "AZ-900 behaald" in prompt
    assert "kubernetes" in prompt


def test_the_precomputed_answer_is_kept_out(client, llm):
    """Aggregates are step 6's answer. Handing them to step -1 would settle the argument
    the demo exists to have."""
    client.post("/api/context", json={"question": "Hoeveel credits?"})
    _, prompt = next((c for c in llm.prompts if c[0] == "longcontext"), (None, ""))
    assert "Huidig saldo" not in prompt


def test_it_reports_what_the_call_cost(client):
    body = client.post("/api/context", json={"question": "Wie heeft AZ-900?"}).json()
    assert body["usage"]["input_tokens"] == 262_000
    assert body["usage"]["cost_usd"] == 1.31
    assert body["chunks"] == 2


def test_a_prepared_question_is_judged_by_the_critic(client):
    body = client.post(
        "/api/context", json={"question": "Ik wil AZ-900 halen, wie heeft dat certificaat al?"}
    ).json()
    assert body["critique"] == [{"ok": True, "label": "Igor genoemd"}]


def test_an_unprepared_question_has_no_critic(client):
    body = client.post("/api/context", json={"question": "iets anders"}).json()
    assert body["critique"] is None


def test_citations_resolve_against_the_whole_corpus(client):
    body = client.post("/api/context", json={"question": "Wie heeft AZ-900?"}).json()
    assert body["citations"] == [
        {"marker": 1, "chunk_id": "a", "title": "Igor", "location": "cv.pdf > p. 1"}
    ]


def test_a_cache_miss_with_no_credential_is_a_message_not_a_crash():
    class Offline:
        def complete_with_usage(self, system, prompt, **kwargs):
            raise NoAnswerAvailable("no cached answer")

        complete = complete_with_usage

    body = build_client(Offline()).post("/api/context", json={"question": "x"}).json()
    assert "no cached answer" in body["error"]
