from __future__ import annotations

from pathlib import Path

import numpy as np

from rag.ingest import read_chunks, write_chunks
from rag.models import Chunk

CHUNKS = "chunks.jsonl"
EMBEDDINGS = "embeddings.npy"
PROJECTION = "projection.npy"


def save_artefacts(
    directory: Path, chunks: list[Chunk], vectors: np.ndarray, projection: np.ndarray
) -> None:
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    write_chunks(chunks, directory / CHUNKS)
    np.save(directory / EMBEDDINGS, vectors)
    np.save(directory / PROJECTION, projection)


def load_artefacts(directory: Path) -> tuple[list[Chunk], np.ndarray, np.ndarray]:
    directory = Path(directory)
    for name in (CHUNKS, EMBEDDINGS, PROJECTION):
        if not (directory / name).exists():
            raise FileNotFoundError(
                f"{directory / name} is missing. Run: uv run python scripts/build_index.py"
            )
    return (
        read_chunks(directory / CHUNKS),
        np.load(directory / EMBEDDINGS),
        np.load(directory / PROJECTION),
    )
