from __future__ import annotations

import re

from rag.models import Citation, Scored

SYSTEM = """You answer questions about a consultancy from the numbered sources supplied.

Use only what the sources say. Cite every claim with the source number in square
brackets, like [2]. If the sources do not contain the answer, say so plainly and stop —
a refusal is more useful than a guess."""

MARKER = re.compile(r"\[(\d+)\]")


def _format_sources(candidates: list[Scored]) -> str:
    return "\n\n".join(
        f"[{i}] {s.chunk.title} — {s.chunk.location}\n{s.chunk.text}"
        for i, s in enumerate(candidates, start=1)
    )


def generate_answer(llm, question: str, candidates: list[Scored], **kwargs) -> str:
    if not candidates:
        return "Nothing in the corpus matched that question."
    prompt = f"Sources:\n\n{_format_sources(candidates)}\n\nQuestion: {question}"
    return llm.complete(SYSTEM, prompt, label="answer", **kwargs).strip()


def extract_citations(answer: str, candidates: list[Scored]) -> list[Citation]:
    citations: list[Citation] = []
    seen: set[int] = set()
    for match in MARKER.finditer(answer):
        marker = int(match.group(1))
        if marker in seen or not 1 <= marker <= len(candidates):
            continue
        seen.add(marker)
        chunk = candidates[marker - 1].chunk
        citations.append(
            Citation(
                marker=marker,
                chunk_id=chunk.id,
                title=chunk.title,
                location=chunk.location,
            )
        )
    return citations
