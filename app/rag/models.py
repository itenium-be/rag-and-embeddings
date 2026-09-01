"""Pure data types. Imports nothing else from `rag`, so every module can use them."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Chunk:
    id: str
    text: str
    source: str
    source_type: str  # policy | cv | project | assignment | credit | aggregate
    title: str
    location: str
    metadata: dict = field(default_factory=dict)


@dataclass(frozen=True)
class Scored:
    chunk: Chunk
    score: float
    # Rank at each stage the chunk passed through, 1-based: {"dense": 12, "rerank": 1}.
    # This is what makes a technique's effect visible on the projector.
    ranks: dict[str, int] = field(default_factory=dict)


@dataclass(frozen=True)
class Citation:
    marker: int
    chunk_id: str
    title: str
    location: str


@dataclass(frozen=True)
class Check:
    """One fact from the reference answer, and whether the answer under review has it."""

    ok: bool
    label: str


@dataclass(frozen=True)
class Config:
    dense: bool = True
    bm25: bool = False
    rerank: bool = False
    rewrite: bool = False
    citations: bool = False
    # Lets precomputed summary chunks into retrieval. Off for the first five steps so
    # the room sees the ledger fail before it sees structure fix it.
    aggregates: bool = False
    top_k: int = 50  # retrieve wide
    top_n: int = 5   # keep few


@dataclass(frozen=True)
class Result:
    question: str
    rewritten: str | None
    candidates: list[Scored]
    used: list[Scored]
    answer: str
    citations: list[Citation]


@dataclass(frozen=True)
class WizardStep:
    number: int
    name: str
    blurb: str
    config: Config


WIZARD_STEPS: list[WizardStep] = [
    WizardStep(
        1,
        "Naive",
        "Embed the question, return the nearest chunks.",
        Config(),
    ),
    WizardStep(
        2,
        "Hybrid search",
        "Run keyword search (az-900) alongside meaning search (vector) and merge the two.",
        Config(bm25=True),
    ),
    WizardStep(
        3,
        "Reranking",
        "Fetch 50 candidates, let a slower model re-sort them, keep 5.",
        Config(bm25=True, rerank=True),
    ),
    WizardStep(
        4,
        "Query rewriting",
        "Broaden the question before searching for it.",
        Config(bm25=True, rerank=True, rewrite=True),
    ),
    WizardStep(
        5,
        "Citations",
        "Track which chunk every claim came from.",
        Config(bm25=True, rerank=True, rewrite=True, citations=True),
    ),
    WizardStep(
        6,
        "Structure",
        "Compute the answer at ingest time instead of retrieving it. "
        "This is not a retrieval technique — it is the next session.",
        Config(bm25=True, rerank=True, rewrite=True, citations=True, aggregates=True),
    ),
]
