"""The session's thesis as an assertion.

Marked slow: it needs the real embedding and reranker models and a built index.
Run it before writing slides, and again the morning of the talk.
"""

from pathlib import Path

import pytest
import yaml

from rag.app import build_engine
from rag.models import WIZARD_STEPS

APP = Path(__file__).resolve().parents[1]
QUESTIONS = yaml.safe_load((APP / "questions.yaml").read_text(encoding="utf-8"))

pytestmark = pytest.mark.slow


@pytest.fixture(scope="module")
def engine():
    return build_engine(APP / "data" / "index", APP / "data" / "cache")


def _passes(check: dict, result) -> bool:
    value = check["value"].lower()
    if check["type"] == "first":
        top = result.used[0].chunk if result.used else None
        return bool(top) and value in f"{top.title} {top.text}".lower()
    return any(value in f"{s.chunk.title} {s.chunk.text}".lower() for s in result.used)


@pytest.mark.parametrize("spec", QUESTIONS, ids=[q["id"] for q in QUESTIONS])
@pytest.mark.parametrize("step", WIZARD_STEPS, ids=[f"step{s.number}" for s in WIZARD_STEPS])
def test_scoreboard(engine, spec, step):
    result = engine.run(spec["question"], step.config)
    expected = spec["steps"][step.number]
    actual = _passes(spec["check"], result)
    assert actual == expected, (
        f"{spec['id']} at step {step.number} ({step.name}): "
        f"expected {'pass' if expected else 'fail'}, got {'pass' if actual else 'fail'}"
    )
