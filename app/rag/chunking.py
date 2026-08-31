"""Recursive character splitting — the index-card metaphor from the session outline."""

from __future__ import annotations

import hashlib

SEPARATORS = ["\n\n", "\n", ". ", " "]


def chunk_id(source: str, ordinal: int, text: str) -> str:
    # Content is part of the id so a re-ingest after an edit produces a new id
    # rather than silently reusing a stale embedding.
    raw = f"{source}\x00{ordinal}\x00{text}".encode()
    return hashlib.sha256(raw).hexdigest()[:16]


def _split_on(text: str, separator: str, size: int) -> list[str]:
    pieces = text.split(separator)
    out: list[str] = []
    current = ""
    for piece in pieces:
        candidate = piece if not current else current + separator + piece
        if len(candidate) <= size:
            current = candidate
        else:
            if current:
                out.append(current)
            current = piece
    if current:
        out.append(current)
    return out


def split_text(text: str, *, size: int = 800, overlap: int = 100) -> list[str]:
    text = text.strip()
    if not text:
        return []
    if len(text) <= size:
        return [text]

    parts = [text]
    for separator in SEPARATORS:
        if all(len(p) <= size for p in parts):
            break
        expanded: list[str] = []
        for part in parts:
            expanded.extend(_split_on(part, separator, size) if len(part) > size else [part])
        parts = expanded

    # Anything still oversized has no separator left to break on.
    hard: list[str] = []
    for part in parts:
        while len(part) > size:
            hard.append(part[:size])
            part = part[size:]
        if part:
            hard.append(part)

    if overlap <= 0 or len(hard) == 1:
        return [p.strip() for p in hard if p.strip()]

    with_overlap = [hard[0]]
    for previous, part in zip(hard, hard[1:]):
        with_overlap.append(previous[-overlap:] + " " + part)
    return [p.strip() for p in with_overlap if p.strip()]
