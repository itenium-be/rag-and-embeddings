"""Fill the answer cache before the talk.

Every question at every wizard step. After this runs, the scripted demo makes no
network calls at all, which is also what stops a 'failing' question from accidentally
succeeding live.
"""

from __future__ import annotations

import sys
from pathlib import Path

APP = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(APP))

import yaml  # noqa: E402

from rag.app import build_engine, load_projection  # noqa: E402
from rag.critic import critique  # noqa: E402
from rag.longcontext import answer_from_corpus, build_corpus  # noqa: E402
from rag.models import WIZARD_STEPS  # noqa: E402


def tally(engine, spec, answer) -> str:
    checks = critique(engine.llm, spec["question"], spec["answer"], answer)
    return f"{sum(c.ok for c in checks)}/{len(checks)}" if checks else "—"


def main() -> None:
    engine = build_engine()
    corpus = build_corpus(load_projection()[0])
    specs = yaml.safe_load((APP / "questions.yaml").read_text(encoding="utf-8"))
    for spec in specs:
        answer, usage = answer_from_corpus(engine.llm, spec["question"], corpus)
        cost = f" · ${usage['cost_usd']:.2f}" if usage.get("cost_usd") is not None else ""
        print(f"  {spec['id']} · step -1 Context · critic {tally(engine, spec, answer)}{cost}")
        for step in WIZARD_STEPS:
            result = engine.run(spec["question"], step.config)
            verdict = tally(engine, spec, result.answer)
            print(f"  {spec['id']} · step {step.number} {step.name} · critic {verdict}")
    print(f"\nWarmed {len(specs) * (len(WIZARD_STEPS) + 1)} entries.")


if __name__ == "__main__":
    main()
