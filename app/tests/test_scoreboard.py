"""The session's thesis as an assertion.

Marked slow: it needs the real embedding and reranker models and a built index.
Run it before writing slides, and again the morning of the talk.
"""

from pathlib import Path

import pytest
import yaml

from rag.app import build_engine
from rag.critic import critique
from rag.models import WIZARD_STEPS

APP = Path(__file__).resolve().parents[1]
QUESTIONS = yaml.safe_load((APP / "questions.yaml").read_text(encoding="utf-8"))

pytestmark = pytest.mark.slow


@pytest.fixture(scope="module")
def engine():
    # Whichever corpus has been built: the real one when it exists, the committed
    # sample otherwise. Pinning this to the sample silently measured the wrong corpus.
    return build_engine(cache_dir=APP / "data" / "cache")


def _verdict(spec: dict, result, llm) -> bool | str:
    check = spec["check"]
    if check["type"] == "refuses":
        # The only check that reads the answer: a question the corpus cannot answer has
        # no correct chunk, so there is nothing in `result.used` to assert on. The judge
        # scores the answer against a reference that says so. Matching refusal phrasings
        # with a regex does not survive a model that refuses in two languages.
        #
        # An empty verdict is a failure, not a pass: critique() swallows its own errors
        # so the demo survives them, and a silent judge would otherwise score green.
        checks = critique(llm, spec["question"], spec["answer"], result.answer)
        return bool(checks) and all(c.ok for c in checks)

    if check["type"] == "everyone":
        # Who came back, not how often the string did. Five CVs contain "AZ-900"; one of
        # them is a Udemy exam-prep course, so a substring count scores a near-miss as a
        # hit and cannot tell three of the four holders from all four.
        retrieved = {s.chunk.title for s in result.used}
        found = [name for name in check["values"] if name in retrieved]
        if len(found) == len(check["values"]):
            return True
        # Most of them is the honest verdict for hybrid search here: a real improvement
        # over naive, and still the wrong answer to give a colleague.
        return "partial" if len(found) * 2 > len(check["values"]) else False

    # Precision, not presence. Hybrid search takes the AZ-900 question from one correct
    # CV in four to three, and a bare substring test cannot tell those two apart.
    #
    # `field: title` asks which document came back rather than which text mentions it.
    # These policies cross-reference each other by name, so a substring test over the text
    # counts a document that merely points at the answer as the answer.
    value = check["value"].lower()
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
    actual = _verdict(spec, result, engine.llm)
    assert actual == expected, (
        f"{spec['id']} at step {step.number} ({step.name}): "
        f"expected {expected!r}, got {actual!r}"
    )
