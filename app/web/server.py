from __future__ import annotations

from dataclasses import asdict
from pathlib import Path

import numpy as np
import yaml
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from rag.llm import NoAnswerAvailable
from rag.models import Chunk, Config, Result, WIZARD_STEPS
from rag.pipeline import Engine

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


def _scored_json(scored) -> dict:
    return {
        "id": scored.chunk.id,
        "title": scored.chunk.title,
        "location": scored.chunk.location,
        "source_type": scored.chunk.source_type,
        "text": scored.chunk.text,
        "score": scored.score,
        "ranks": scored.ranks,
    }


def _result_json(result: Result) -> dict:
    return {
        "question": result.question,
        "rewritten": result.rewritten,
        "answer": result.answer,
        "citations": [asdict(c) for c in result.citations],
        "used": [_scored_json(s) for s in result.used],
        "candidates": [_scored_json(s) for s in result.candidates[:20]],
    }


def create_app(engine: Engine, chunks: list[Chunk], projection: np.ndarray) -> FastAPI:
    app = FastAPI(title="RAG demo")

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
        specs = yaml.safe_load(QUESTIONS_FILE.read_text(encoding="utf-8"))
        return [
            {"id": s["id"], "question": s["question"], "steps": s["steps"]} for s in specs
        ]

    @app.post("/api/ask")
    def ask(request: AskRequest) -> dict:
        try:
            result = engine.run(request.question, _config_for(request))
        except NoAnswerAvailable as exc:
            return {"error": str(exc)}
        except Exception as exc:
            # A live LLM call can fail for reasons other than a missing credential
            # (e.g. no API credit) — the room must see a message, never a stack trace.
            return {"error": str(exc)}
        return _result_json(result)

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
    from rag.app import APP_DIR, CACHE_DIR, build_engine, load_projection

    index_dir = APP_DIR / "data" / "index-real"
    if not index_dir.is_dir():
        index_dir = APP_DIR / "data" / "index"

    chunks, projection = load_projection(index_dir)
    return create_app(build_engine(index_dir, CACHE_DIR), chunks, projection)
