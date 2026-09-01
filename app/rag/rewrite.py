"""Step-back prompting: the question as typed is often a bad search query."""

from __future__ import annotations

SYSTEM = """You rewrite questions into better search queries for a document search over
consultant CVs, project sheets, HR records and company policies.

Broaden an over-specific question into the more general one that has to be answered
first. Split a compound question into its parts. Keep every proper noun, product name
and certification code from the original exactly as written.

Start with the question as it was asked, word for word, and add the broader or split
phrasings after it. A rewrite that only asks the general question retrieves the policy
that describes a list instead of the document that is the list.

Reply with the rewritten query and nothing else."""


def rewrite_query(llm, question: str) -> str:
    rewritten = llm.complete(SYSTEM, f"Question: {question}", label="rewrite").strip()
    return rewritten or question
