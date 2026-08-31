from rag.chunking import chunk_id, split_text


def test_short_text_is_one_chunk():
    assert split_text("hello world", size=800, overlap=100) == ["hello world"]


def test_long_text_splits_on_paragraph_boundaries():
    text = "\n\n".join(f"Paragraph {i}. " + "word " * 40 for i in range(6))
    parts = split_text(text, size=400, overlap=50)
    assert len(parts) > 1
    # A chunk carries its predecessor's tail, so the ceiling is size + overlap.
    assert all(len(p) <= 400 + 50 + 1 for p in parts)


def test_consecutive_chunks_overlap():
    text = " ".join(f"w{i}" for i in range(400))
    parts = split_text(text, size=300, overlap=60)
    assert len(parts) > 1
    tail = parts[0][-40:]
    assert tail in parts[1]


def test_no_content_is_dropped():
    text = " ".join(f"w{i}" for i in range(400))
    parts = split_text(text, size=300, overlap=60)
    joined = " ".join(parts)
    for i in range(400):
        assert f"w{i}" in joined


def test_chunk_id_is_deterministic():
    assert chunk_id("cv/ana.md", 3, "text") == chunk_id("cv/ana.md", 3, "text")


def test_chunk_id_varies_with_every_input():
    base = chunk_id("cv/ana.md", 3, "text")
    assert chunk_id("cv/bram.md", 3, "text") != base
    assert chunk_id("cv/ana.md", 4, "text") != base
    assert chunk_id("cv/ana.md", 3, "other") != base
