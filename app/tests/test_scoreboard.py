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
    # Whichever corpus has been built: the real one when it exists, the committed
    # sample otherwise. Pinning this to the sample silently measured the wrong corpus.
    return build_engine(cache_dir=APP / "data" / "cache")


def _passes(check: dict, result) -> bool:
    value = check["value"].lower()
    top = result.used[0].chunk if result.used else None
    if check["type"] == "first":
        # Both halves matter, and each was learned from a false positive. Matching only
        # the text let a credit-ledger row for attending a Kubernetes event answer "who
        # can help me with Kubernetes". Matching only the kind of chunk let a CV that
        # never mentions Kubernetes do the same.
        if not top or value not in f"{top.title} {top.text}".lower():
            return False
        wanted_type = check.get("source_type")
        return wanted_type is None or top.source_type == wanted_type
    # Precision, not presence. Hybrid search takes the AZ-900 question from one correct
    # CV in five to four, and a bare substring test cannot tell those two apart.
    #
    # `field: title` asks which document came back rather than which text mentions it.
    # The laptop policy says "met uitzondering van de wagens en de Car Policy", and that
    # cross-reference was being counted as a car-policy result.
    field = check.get("field", "any")
    def blob(chunk):
        return chunk.title.lower() if field == "title" else f"{chunk.title} {chunk.text}".lower()

    matches = sum(1 for s in result.used if value in blob(s.chunk))
    return matches >= check.get("min_matches", 1)


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
