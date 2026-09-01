import numpy as np
import pytest
from fastapi.testclient import TestClient

from rag.index import Bm25Index, DenseIndex
from rag.models import Chunk
from rag.pipeline import Engine
from web.server import create_app


class StubLLM:
    def complete(self, system: str, prompt: str, **kwargs) -> str:
        label = kwargs.get("label")
        if label == "checklist":
            return "1. Igor Romy genoemd\n2. Jos Van Loock genoemd"
        if label == "critic":
            return "1 PASS\n2 FAIL"
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


def test_questions_report_the_step_that_first_improves_them(client):
    by_id = {q["id"]: q for q in client.get("/api/questions").json()}
    assert by_id["ai-tools"]["demo_at"] == 1
    assert by_id["creditsaldo"]["demo_at"] == 6


def test_the_long_context_baseline_is_never_the_step_a_question_demonstrates(client):
    """Step -1 demonstrates no technique; it is what the techniques are measured against."""
    assert all(q["demo_at"] != -1 for q in client.get("/api/questions").json())


def test_questions_carry_a_long_context_verdict(client):
    assert all("-1" in q["steps"] for q in client.get("/api/questions").json())


def test_a_question_demos_at_the_step_that_partly_fixes_it(client):
    az = {q["id"]: q for q in client.get("/api/questions").json()}["az-900"]
    assert az["demo_at"] == 2, "hybrid search is where AZ-900 stops being useless"
    assert az["steps"]["2"] == "partial"
    assert az["steps"]["3"] is True


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


def test_ask_returns_the_query_vector_and_a_vector_per_chunk(client):
    body = client.post("/api/ask", json={"question": "AZ-204", "step": 1}).json()
    assert body["dims"] == 2
    assert body["query_vector"] == [1.0, 0.0]
    assert body["used"][0]["vector"] == [1.0, 0.0]
    assert body["used"][0]["similarity"] == 1.0


def test_ask_returns_candidates_reranking_dropped(client):
    body = client.post(
        "/api/ask",
        json={"question": "AZ-204", "config": {"dense": True, "rerank": True, "top_n": 1}},
    ).json()
    used = {c["id"] for c in body["used"]}
    assert len(used) == 1
    # The grid greys these out. Without them the room cannot see what reranking removed.
    assert [c["id"] for c in body["candidates"] if c["id"] not in used]


def test_static_assets_are_served(client):
    assert client.get("/static/favicon.ico").status_code == 200
    assert client.get("/static/logo.svg").status_code == 200


def test_map_clusters_endpoint_names_the_blobs(client):
    clusters = client.get("/api/map/clusters").json()
    assert [c["label"] for c in clusters] == ["CVs"]
    assert clusters[0]["count"] == 2


def test_ask_logs_the_question_and_what_the_pipeline_did(client, caplog):
    with caplog.at_level("INFO", logger="web.server"):
        client.post("/api/ask", json={"question": "AZ-204", "step": 1})
    text = caplog.text
    assert "AZ-204" in text
    assert "step 1" in text
    assert "candidates" in text


def test_a_prepared_question_is_judged_against_its_reference(client):
    question = "Ik wil AZ-900 halen, wie heeft dat certificaat al?"
    body = client.post("/api/ask", json={"question": question, "step": 1}).json()
    assert body["critique"] == [
        {"ok": True, "label": "Igor Romy genoemd"},
        {"ok": False, "label": "Jos Van Loock genoemd"},
    ]


def test_a_question_nobody_prepared_has_no_reference_to_judge_against(client):
    body = client.post("/api/ask", json={"question": "AZ-204", "step": 1}).json()
    assert body["critique"] is None


def test_the_critic_verdict_is_logged(client, caplog):
    question = "Ik wil AZ-900 halen, wie heeft dat certificaat al?"
    with caplog.at_level("INFO", logger="web.server"):
        client.post("/api/ask", json={"question": question, "step": 1})
    assert "critic" in caplog.text
    assert "1/2" in caplog.text


def test_questions_carry_the_steps_that_needed_tuning(client):
    by_id = {q["id"]: q for q in client.get("/api/questions").json()}
    note = by_id["ai-tools"]["note"]
    assert note["steps"] == [4, 5, 6]
    assert note["text"]
    assert by_id["creditsaldo"]["note"] is None
