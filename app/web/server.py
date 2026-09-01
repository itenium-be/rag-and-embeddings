from __future__ import annotations

import logging
import threading
import time
from dataclasses import asdict
from pathlib import Path

import numpy as np
import yaml
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from rag.critic import critique
from rag.llm import NoAnswerAvailable
from rag.models import Chunk, Config, Result, WIZARD_STEPS
from rag.pipeline import Engine
from web.clusters import cluster_ellipses
from web.trace import format_critique, format_question, format_result, install_console_logging

log = logging.getLogger(__name__)

STATIC = Path(__file__).resolve().parent / "static"
QUESTIONS_FILE = Path(__file__).resolve().parents[1] / "questions.yaml"


class AskRequest(BaseModel):
    question: str
    step: int | None = None
    config: dict | None = None


class MapQuery(BaseModel):
    question: str
    k: int = 5


def _config_for(request: AskRequest) -> Config:
    if request.config is not None:
        return Config(**request.config)
    if request.step is not None:
        return WIZARD_STEPS[request.step - 1].config
    return Config()


def _questions() -> list[dict]:
    return yaml.safe_load(QUESTIONS_FILE.read_text(encoding="utf-8"))


def _reference_for(question: str) -> str | None:
    """The known-correct answer for a prepared question, if this is one of them.

    Read per request rather than at startup: the reference is what the critic judges
    against, and rewording it between two questions must not need a restart.
    """
    for spec in _questions():
        if spec["question"] == question:
            return spec.get("answer")
    return None


def _preview(vector: np.ndarray) -> list[float]:
    return [round(float(v), 6) for v in vector]


def _scored_json(scored, query_vector: np.ndarray, vector_of: dict) -> dict:
    vector = vector_of.get(scored.chunk.id)
    return {
        "id": scored.chunk.id,
        "title": scored.chunk.title,
        "location": scored.chunk.location,
        "source_type": scored.chunk.source_type,
        "text": scored.chunk.text,
        "score": scored.score,
        "ranks": scored.ranks,
        "vector": _preview(vector) if vector is not None else [],
        # Both sides are normalised at embed time, so the dot product is the cosine.
        "similarity": round(float(vector @ query_vector), 4) if vector is not None else None,
    }


def _result_json(result: Result, query_vector: np.ndarray, vector_of: dict) -> dict:
    return {
        "question": result.question,
        "rewritten": result.rewritten,
        "answer": result.answer,
        "citations": [asdict(c) for c in result.citations],
        "dims": int(query_vector.shape[0]),
        "query_vector": _preview(query_vector),
        "used": [_scored_json(s, query_vector, vector_of) for s in result.used],
        "candidates": [_scored_json(s, query_vector, vector_of) for s in result.candidates[:20]],
    }


def create_app(engine: Engine, chunks: list[Chunk], projection: np.ndarray) -> FastAPI:
    app = FastAPI(title="RAG demo")
    vector_of = {c.id: v for c, v in zip(engine.dense.chunks, engine.dense.vectors)}

    @app.get("/")
    def index() -> FileResponse:
        return FileResponse(STATIC / "index.html")

    app.mount("/static", StaticFiles(directory=STATIC), name="static")

    @app.get("/api/steps")
    def steps() -> list[dict]:
        return [
            {
                "number": s.number,
                "name": s.name,
                "blurb": s.blurb,
                "config": asdict(s.config),
            }
            for s in WIZARD_STEPS
        ]

    @app.get("/api/questions")
    def questions() -> list[dict]:
        return [
            {
                "id": s["id"],
                "question": s["question"],
                "steps": s["steps"],
                # The step this question exists to demonstrate: the first one whose
                # verdict is better than a flat failure, so a question that a technique
                # only partly fixes still opens on that technique. Derived rather than
                # declared, so it cannot drift from the scoreboard.
                "demo_at": next((n for n in sorted(s["steps"]) if s["steps"][n]), None),
                "note": s.get("note"),
            }
            for s in _questions()
        ]

    @app.post("/api/ask")
    def ask(request: AskRequest) -> dict:
        config = _config_for(request)
        step = None if request.config is not None else request.step
        log.info(format_question(request.question, step, config))
        started = time.perf_counter()
        try:
            result = engine.run(request.question, config)
        except NoAnswerAvailable as exc:
            log.info("   failed    %s", exc)
            return {"error": str(exc)}
        except Exception as exc:
            # A live LLM call can fail for reasons other than a missing credential
            # (e.g. no API credit) — the room must see a message, never a stack trace.
            log.info("   failed    %s", exc)
            return {"error": str(exc)}
        for line in format_result(result, config, time.perf_counter() - started):
            log.info(line)

        reference = _reference_for(request.question)
        checks = critique(engine.llm, request.question, reference, result.answer) if reference else []
        if reference:
            log.info(format_critique(checks))

        # The rewritten query is what retrieval actually saw, so it is the vector the
        # room should be looking at.
        query_vector = engine.embed_query(result.rewritten or result.question)
        return {
            **_result_json(result, query_vector, vector_of),
            "critique": [asdict(c) for c in checks] if reference else None,
        }

    @app.get("/api/map")
    def map_points() -> list[dict]:
        return [
            {
                "id": chunk.id,
                "x": float(point[0]),
                "y": float(point[1]),
                "title": chunk.title,
                "source_type": chunk.source_type,
                "text": chunk.text[:400],
            }
            for chunk, point in zip(chunks, projection)
        ]

    @app.get("/api/map/clusters")
    def map_clusters() -> list[dict]:
        return cluster_ellipses(chunks, projection)

    @app.post("/api/map/query")
    def map_query(request: MapQuery) -> dict:
        vector = engine.embed_query(request.question)
        hits = engine.dense.search(vector, request.k)
        neighbour_ids = [chunk.id for chunk, _ in hits]
        # Place the query where its neighbours are: the projection is fitted on the
        # corpus and cannot transform an unseen point in a way the room would trust.
        index = {c.id: i for i, c in enumerate(chunks)}
        points = np.array([projection[index[cid]] for cid in neighbour_ids])
        centre = points.mean(axis=0)
        return {
            "x": float(centre[0]),
            "y": float(centre[1]),
            "neighbours": neighbour_ids,
        }

    return app


def build() -> FastAPI:
    install_console_logging()

    from rag.app import APP_DIR, CACHE_DIR, build_engine, load_projection, warm_models

    index_dir = APP_DIR / "data" / "index-real"
    if not index_dir.is_dir():
        index_dir = APP_DIR / "data" / "index"

    chunks, projection = load_projection(index_dir)
    engine = build_engine(index_dir, CACHE_DIR)
    # On a thread, so the page is up while the weights load rather than after.
    threading.Thread(target=warm_models, args=(engine,), daemon=True).start()
    return create_app(engine, chunks, projection)
