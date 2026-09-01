"""Judges an answer against the reference answer in questions.yaml.

The room can read whether an answer sounds right; it cannot read whether it is right.

Two calls, not one. The checklist is derived from the reference alone, so every step is
scored against the same items and the ticks can be compared as the room walks the steps;
asking for checklist and verdict together produced a different list per step, which
compares nothing. It also means the checklist is one cache entry per question rather than
one per question and step.
"""

from __future__ import annotations

import logging
import re

from rag.models import Check

log = logging.getLogger(__name__)

CHECKLIST_SYSTEM = """You turn a reference answer into the checklist a correct answer has
to satisfy.

Write as many items as the reference states facts, at most six. A reference that states
one fact gets one item: never split a fact in two, and never pad the list with detail the
reference leaves out. Each item is one fact, at most eight words, stated as the fact
itself rather than as an instruction, and written in the language of the reference.
Phrase an item about a claim that must NOT be made so that an answer which stays silent
about it satisfies the item ("noemt X niet als houder").

Reply with one item per line, numbered `1.`, `2.`, and nothing else."""

JUDGE_SYSTEM = """You check an answer against a numbered checklist.

For each item, decide whether the answer satisfies it. Judge the answer as a reply to the
question: it may leave out what the question already supplied, and naming nobody is right
when the question named the person. Judge only what the answer says beyond that — an
answer that is vague where the item is specific does not satisfy it.

Reply with one line per item, `<number> PASS` or `<number> FAIL`, and nothing else."""

ITEM = re.compile(r"^\s*\d+[.)]\s*(.+?)\s*$", re.MULTILINE)
VERDICT = re.compile(r"^\s*(\d+)[.)\s]+(PASS|FAIL)\b", re.MULTILINE)


def parse_items(reply: str) -> list[str]:
    return ITEM.findall(reply)


def parse_verdicts(reply: str, items: list[str]) -> list[Check]:
    verdicts = {int(n): v == "PASS" for n, v in VERDICT.findall(reply)}
    return [
        Check(ok=verdicts[i], label=item)
        for i, item in enumerate(items, start=1)
        if i in verdicts
    ]


def checklist(llm, reference: str) -> list[str]:
    return parse_items(llm.complete(CHECKLIST_SYSTEM, reference, label="checklist"))


def critique(llm, question: str, reference: str, answer: str) -> list[Check]:
    if not answer.strip():
        return []
    try:
        items = checklist(llm, reference)
        if not items:
            return []
        numbered = "\n".join(f"{i}. {item}" for i, item in enumerate(items, start=1))
        reply = llm.complete(
            JUDGE_SYSTEM,
            f"Question:\n\n{question}\n\nChecklist:\n\n{numbered}\n\nAnswer:\n\n{answer}",
            label="critic"
        )
        return parse_verdicts(reply, items)
    except Exception as exc:
        # The critic is commentary on the demo, not the demo. A missing verdict costs a
        # slide; a stack trace costs the room.
        log.info("   %-9s %s", "critic", exc)
        return []
