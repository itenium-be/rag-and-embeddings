"""Build every artefact the app loads at startup. Run once, before the talk."""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np

APP = Path(__file__).resolve().parents[1]


def project(vectors: np.ndarray) -> np.ndarray:
    import umap

    # A fixed seed so the map looks the same in rehearsal as it does on the day.
    reducer = umap.UMAP(n_components=2, metric="cosine", random_state=42)
    return reducer.fit_transform(vectors).astype(np.float32)


def main() -> None:
    import sys

    sys.path.insert(0, str(APP))
    from rag.embed import embed_passages
    from rag.ingest import ingest_corpus
    from rag.store import save_artefacts

    parser = argparse.ArgumentParser()
    parser.add_argument("--corpus", type=Path, default=None)
    parser.add_argument("--out", type=Path, default=APP / "data" / "index")
    args = parser.parse_args()

    corpus = args.corpus or (
        APP / "data" / "raw" if (APP / "data" / "raw").is_dir() else APP / "sample"
    )
    print(f"Ingesting {corpus}")
    chunks = ingest_corpus(corpus)
    if not chunks:
        raise SystemExit(
            f"No documents found under {corpus}. Expected policies/, projects/, cvs/ "
            "or bamboo.json."
        )
    print(f"{len(chunks)} chunks")

    vectors = embed_passages([c.text for c in chunks])
    projection = project(vectors)
    save_artefacts(args.out, chunks, vectors, projection)
    print(f"Wrote artefacts to {args.out}")


if __name__ == "__main__":
    main()
