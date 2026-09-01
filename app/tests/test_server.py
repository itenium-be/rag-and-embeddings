import numpy as np
import pytest
from fastapi.testclient import TestClient

from rag.index import Bm25Index, DenseIndex
from rag.models import Chunk
from rag.pipeline import Engine
from web.server import create_app


class StubLLM:
    def complete(self, system: str, prompt: str, **kwargs) -> str:
        return "An answer [1]."


class NullReranker:
    def score(self, query: str, texts: list[str]) -> list[float]:
        return [0.0] * len(texts)


@pytest.fixture
def client():
    chunks = [
        Chunk(id="a", text="AZ-204 azure", source="s", source_type="cv", title="Bram", location="l"),
        Chunk(id="b", text="kubernetes", source="s", source_type="cv", title="Dries", location="l"),
    ]
    vectors = np.array([[1.0, 0.0], [0.0, 1.0]], dtype=np.float32)
    engine = Engine(
        dense=DenseIndex(chunks, vectors),
        bm25=Bm25Index(chunks),
        reranker=NullReranker(),
        llm=StubLLM(),
        embed_query=lambda _: np.array([1.0, 0.0], dtype=np.float32),
    )
    projection = np.array([[0.1, 0.2], [0.3, 0.4]], dtype=np.float32)
    return TestClient(create_app(engine, chunks, projection))


def test_steps_endpoint_returns_the_six_wizard_steps(client):
    steps = client.get("/api/steps").json()
    assert [s["number"] for s in steps] == [1, 2, 3, 4, 5, 6]
    assert steps[1]["config"]["bm25"] is True


def test_questions_endpoint_returns_the_five_questions(client):
    questions = client.get("/api/questions").json()
    assert len(questions) == 5
    assert all("question" in q for q in questions)


def test_ask_returns_answer_used_and_candidates(client):
    body = client.post("/api/ask", json={"question": "AZ-204", "step": 1}).json()
    assert body["answer"] == "An answer [1]."
    assert body["used"]
    assert "ranks" in body["used"][0]


def test_ask_accepts_a_raw_config_from_the_advanced_panel(client):
    body = client.post(
        "/api/ask",
        json={"question": "AZ-204", "config": {"dense": True, "bm25": True, "top_n": 1}},
    ).json()
    assert len(body["used"]) == 1


def test_map_returns_a_point_per_chunk(client):
    points = client.get("/api/map").json()
    assert len(points) == 2
    assert {"x", "y", "id", "title", "source_type", "text"} <= set(points[0])


def test_map_query_returns_the_query_point_and_neighbours(client):
    body = client.post("/api/map/query", json={"question": "AZ-204", "k": 1}).json()
    assert "x" in body and "y" in body
    assert body["neighbours"] == ["a"]


def test_index_page_is_served(client):
    assert client.get("/").status_code == 200


def test_static_assets_are_served(client):
    assert client.get("/static/favicon.ico").status_code == 200
    assert client.get("/static/logo.svg").status_code == 200
