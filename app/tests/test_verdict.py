"""The `refuses` check: the one verdict that reads the answer instead of the retrieval.

A question the corpus cannot answer has no correct chunk, so `includes` and `everyone`
have nothing to assert on.
"""

from rag.critic import CHECKLIST_SYSTEM
from tests.test_scoreboard import _verdict

SPEC = {
    "question": "Kan ik een fiets leasen?",
    "answer": "Hier staat niets over in de bronnen.",
    "check": {"type": "refuses"},
}


class StubLLM:
    def __init__(self, items: str = "1. de bronnen bevatten geen antwoord", verdicts: str = "1 PASS"):
        self.items = items
        self.verdicts = verdicts

    def complete(self, system: str, prompt: str, **kwargs) -> str:
        return self.items if system == CHECKLIST_SYSTEM else self.verdicts


class Answered:
    def __init__(self, answer: str) -> None:
        self.answer = answer
        self.used = []


def test_an_answer_that_satisfies_the_reference_refusal_passes():
    result = Answered("Daar staat niets over in de bronnen.")
    assert _verdict(SPEC, result, StubLLM()) is True


def test_an_answer_that_improvises_fails():
    result = Answered("Ja, dat kan via het mobiliteitsbudget.")
    assert _verdict(SPEC, result, StubLLM(verdicts="1 FAIL")) is False


def test_a_judge_that_returned_nothing_is_not_a_pass():
    # critique() swallows its own failures so a missing verdict costs the demo a slide
    # rather than the room. Read as a verdict, that silence would be a green row.
    class Broken:
        def complete(self, system: str, prompt: str, **kwargs) -> str:
            raise RuntimeError("no credential")

    assert _verdict(SPEC, Answered("Daar staat niets over in de bronnen."), Broken()) is False
