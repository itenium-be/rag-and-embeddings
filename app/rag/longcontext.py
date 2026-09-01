"""Step -1: the whole corpus in the prompt, and no retrieval at all.

The baseline the retrieval steps have to beat. If dumping everything answers the five
questions, the rest of the app is machinery nobody needed.

Aggregates are left out. They are step 6's answer computed at ingest time, and letting
them in would hand long context the one answer no retrieval technique can reach.
"""

from __future__ import annotations

import re

from rag.generate import SYSTEM
from rag.models import Chunk

PAGE = re.compile(r"p\. *(\d+)")


def _order(chunk: Chunk) -> tuple[str, int, str]:
    """Group a document's chunks together and put its pages in reading order.

    Page numbers sort numerically or `p. 10` lands before `p. 9`, which would split a
    policy into a shuffle of pages and undo the point of holding the whole corpus.
    """
    page = PAGE.search(chunk.location)
    return (chunk.source, int(page.group(1)) if page else 0, chunk.location)


def build_corpus(chunks: list[Chunk]) -> str:
    retrievable = sorted(
        (c for c in chunks if c.source_type != "aggregate"), key=_order
    )
    if not retrievable:
        raise ValueError("nothing to put in the context window")
    return "\n\n".join(
        f"[{i}] {c.title} — {c.location}\n{c.text}"
        for i, c in enumerate(retrievable, start=1)
    )


def answer(llm, question: str, corpus: str) -> str:
    """The corpus first: it is the same bytes on every question, so it is the prefix a
    cache — the CLI's, or ours on disk — can actually reuse."""
    prompt = f"Sources:\n\n{corpus}\n\nQuestion: {question}"
    return llm.complete(SYSTEM, prompt, label="longcontext", fallback_to=question).strip()
