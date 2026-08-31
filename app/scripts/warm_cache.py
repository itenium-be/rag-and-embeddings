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

from rag.app import build_engine  # noqa: E402
from rag.models import WIZARD_STEPS  # noqa: E402


def main() -> None:
    engine = build_engine()
    specs = yaml.safe_load((APP / "questions.yaml").read_text(encoding="utf-8"))
    for spec in specs:
        for step in WIZARD_STEPS:
            engine.run(spec["question"], step.config)
            print(f"  {spec['id']} · step {step.number} {step.name}")
    print(f"\nWarmed {len(specs) * len(WIZARD_STEPS)} entries.")


if __name__ == "__main__":
    main()
