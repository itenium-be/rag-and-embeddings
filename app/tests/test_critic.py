from rag.critic import (
    CHECKLIST_SYSTEM,
    JUDGE_SYSTEM,
    checklist,
    critique,
    parse_items,
    parse_verdicts,
)
from rag.models import Check

ITEMS = "1. Igor Romy heeft AZ-900\n2. Jos Van Loock heeft AZ-900\n3. noemt Mirko Messina niet"


class StubLLM:
    """Answers the checklist call and the judging call, and remembers both."""

    def __init__(self, items: str = ITEMS, verdicts: str = "1 PASS\n2 FAIL\n3 PASS") -> None:
        self.items = items
        self.verdicts = verdicts
        self.calls: list[tuple[str, str]] = []

    def complete(self, system: str, prompt: str, **kwargs) -> str:
        self.calls.append((system, prompt))
        return self.items if system == CHECKLIST_SYSTEM else self.verdicts


def test_numbered_lines_become_checklist_items():
    assert parse_items("1. Vier houders\n2) Igor Romy genoemd") == ["Vier houders", "Igor Romy genoemd"]


def test_prose_around_the_checklist_is_ignored():
    assert parse_items("Here you go:\n\n1. Vier houders\n\nThat is all.") == ["Vier houders"]


def test_verdicts_are_matched_to_items_by_number():
    checks = parse_verdicts("1 PASS\n2 FAIL", ["een", "twee"])
    assert checks == [Check(ok=True, label="een"), Check(ok=False, label="twee")]


def test_an_item_the_judge_skipped_is_left_out_rather_than_guessed():
    assert parse_verdicts("2 FAIL", ["een", "twee"]) == [Check(ok=False, label="twee")]


def test_the_checklist_is_derived_from_the_reference_alone():
    llm = StubLLM()
    checklist(llm, "Igor Romy heeft AZ-900.")
    system, prompt = llm.calls[0]
    assert system == CHECKLIST_SYSTEM
    # The answer under review must not reach this call: the same reference has to produce
    # the same checklist at every step, and it is cached on the prompt.
    assert prompt == "Igor Romy heeft AZ-900."


def test_the_judge_sees_the_numbered_checklist_and_the_answer():
    llm = StubLLM()
    critique(llm, question="Wie heeft AZ-900?", reference="r", answer="Niemand heeft AZ-900.")
    system, prompt = llm.calls[1]
    assert system == JUDGE_SYSTEM
    assert "Wie heeft AZ-900?" in prompt
    assert "1. Igor Romy heeft AZ-900" in prompt
    assert "Niemand heeft AZ-900." in prompt


def test_critique_returns_a_check_per_checklist_item():
    checks = critique(StubLLM(), question="q", reference="r", answer="a")
    assert [(c.ok, c.label) for c in checks] == [
        (True, "Igor Romy heeft AZ-900"),
        (False, "Jos Van Loock heeft AZ-900"),
        (True, "noemt Mirko Messina niet"),
    ]


def test_an_answer_the_pipeline_could_not_produce_is_not_sent_to_the_critic():
    llm = StubLLM()
    assert critique(llm, question="q", reference="r", answer="  ") == []
    assert llm.calls == []


def test_a_reference_that_yields_no_checklist_is_not_judged():
    llm = StubLLM(items="I cannot do that.")
    assert critique(llm, question="q", reference="r", answer="a") == []
    assert len(llm.calls) == 1


def test_a_critic_that_fails_costs_the_room_nothing():
    class Broken:
        def complete(self, system: str, prompt: str, **kwargs) -> str:
            raise RuntimeError("no credential")

    assert critique(Broken(), question="q", reference="r", answer="a") == []
