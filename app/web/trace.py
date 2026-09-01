"""What the presenter's console shows for every question the room asks.

The lines are split in two because the LLM logs its own cache hits in between: the
question header goes out before the run, the summary after it, so the console reads
in the order the pipeline actually executed.
"""

from __future__ import annotations

import logging
import os

from rag.models import Check, Config, LONG_CONTEXT_STEP, Result, WIZARD_STEPS

TECHNIQUES = ("dense", "bm25", "rerank", "rewrite", "citations", "aggregates")
INDENT = "   "


def _techniques(config: Config) -> str:
    return "+".join(t for t in TECHNIQUES if getattr(config, t)) or "nothing"


def _stage(name: str, detail: str) -> str:
    return f"{INDENT}{name:<9} {detail}"


def format_question(question: str, step: int | None, config: Config | None) -> str:
    if step == LONG_CONTEXT_STEP:
        return f"\nQ  step -1 · Context · no retrieval\n{INDENT}{question}"
    if step is None:
        label = "custom"
    else:
        label = f"step {step} · {WIZARD_STEPS[step - 1].name}"
    return f"\nQ  {label} · {_techniques(config)}\n{INDENT}{question}"


def _thousands(tokens: int) -> str:
    return f"{tokens / 1000:.0f}k" if tokens >= 1000 else str(tokens)


def format_usage(usage: dict, chunks: int, elapsed: float) -> str:
    """What the whole corpus cost to ask once."""
    parts = [f"{chunks} chunks"]
    if usage.get("input_tokens"):
        parts.append(f"{_thousands(usage['input_tokens'])} tokens")
    if usage.get("cache_read_tokens"):
        parts.append(f"cache read {_thousands(usage['cache_read_tokens'])}")
    if usage.get("cost_usd") is not None:
        parts.append(f"${usage['cost_usd']:.2f}")
    parts.append(f"{elapsed:.1f}s")
    return _stage("context", " · ".join(parts))


def _retrieved(result: Result) -> str:
    counts = [
        f"{retriever} {sum(1 for s in result.candidates if retriever in s.ranks)}"
        for retriever in ("dense", "bm25")
        if any(retriever in s.ranks for s in result.candidates)
    ]
    fused = " + ".join(counts) + " → " if counts else ""
    return f"{fused}{len(result.candidates)} candidates"


def _used(result: Result) -> list[str]:
    return [
        f"{INDENT}{' ':<9} {position}. {s.chunk.title} — {s.chunk.location}  "
        + " ".join(f"{stage}#{rank}" for stage, rank in s.ranks.items() if stage != "fused")
        for position, s in enumerate(result.used, start=1)
    ]


def format_result(result: Result, config: Config, elapsed: float) -> list[str]:
    rewrite = f"→ {result.rewritten}" if result.rewritten else "off"
    rerank = f"{len(result.candidates)} → {len(result.used)}" if config.rerank else "off"
    count = len(result.citations)
    citations = f"{count} citation{'s' * (count != 1)}" if config.citations else "citations off"
    return [
        _stage("rewrite", rewrite),
        _stage("retrieve", _retrieved(result)),
        _stage("rerank", rerank),
        _stage("answer", f"{len(result.used)} chunks · {citations} · {elapsed:.1f}s"),
        *_used(result),
    ]


def format_critique(checks: list[Check]) -> str:
    if not checks:
        return _stage("critic", "no verdict")
    passed = sum(1 for c in checks if c.ok)
    verdicts = " · ".join(("\u2714 " if c.ok else "\u2718 ") + c.label for c in checks)
    return _stage("critic", f"{passed}/{len(checks)} · {verdicts}")


def install_console_logging() -> None:
    """Uvicorn only configures its own loggers, and the root logger has no handler."""
    # The hub echoes a `Warning` response header ("set a HF_TOKEN...") through its own
    # logger when it checks the cached model files. It configures that logger the first
    # time it is imported, reading this variable, so setting a level here would be
    # overwritten — the model imports are lazy and happen well after this call.
    os.environ.setdefault("HF_HUB_VERBOSITY", "error")

    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(message)s"))
    for name in ("rag", "web"):
        logger = logging.getLogger(name)
        logger.setLevel(logging.INFO)
        if not logger.handlers:
            logger.addHandler(handler)
