import numpy as np

from rag.models import Chunk
from rag.store import load_artefacts, save_artefacts


def _chunk(cid: str) -> Chunk:
    return Chunk(id=cid, text=cid, source="s", source_type="cv", title=cid, location="l")


def test_round_trip_preserves_chunks_and_vectors(tmp_path):
    chunks = [_chunk("a"), _chunk("b")]
    vectors = np.array([[1.0, 0.0], [0.0, 1.0]], dtype=np.float32)
    projection = np.array([[0.1, 0.2], [0.3, 0.4]], dtype=np.float32)
    save_artefacts(tmp_path, chunks, vectors, projection)

    loaded_chunks, loaded_vectors, loaded_projection = load_artefacts(tmp_path)
    assert [c.id for c in loaded_chunks] == ["a", "b"]
    assert np.allclose(loaded_vectors, vectors)
    assert np.allclose(loaded_projection, projection)


def test_missing_artefacts_name_the_file_and_the_fix(tmp_path):
    import pytest

    with pytest.raises(FileNotFoundError, match="build_index"):
        load_artefacts(tmp_path)
