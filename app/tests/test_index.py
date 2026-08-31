import numpy as np

from rag.index import Bm25Index, DenseIndex, query_terms, tokenize
from rag.models import Chunk


def _chunk(cid: str, text: str) -> Chunk:
    return Chunk(id=cid, text=text, source="s", source_type="cv", title=cid, location="l")


def test_tokenizer_keeps_certification_codes_whole():
    assert "az-204" in tokenize("Holds the AZ-204 certification")
    assert "az-104" not in tokenize("Holds the AZ-204 certification")


def test_bm25_matches_the_exact_code_only():
    chunks = [
        _chunk("a", "Certifications: AZ-104 and AZ-400 for Azure administration"),
        _chunk("b", "Certifications: AZ-204 Developing Solutions for Microsoft Azure"),
        _chunk("c", "Certifications: DP-203 Data Engineering on Microsoft Azure"),
    ]
    hits = Bm25Index(chunks).search("Who has the AZ-204 certification?", k=3)
    assert hits[0][0].id == "b"


def test_bm25_keeps_a_match_whose_idf_is_zero():
    # rank_bm25 gives a term appearing in exactly half the corpus an idf of 0.0, so
    # every score is 0.0 and a score filter would throw the real match away.
    chunks = [_chunk("a", "kubernetes platform"), _chunk("b", "angular frontend")]
    hits = Bm25Index(chunks).search("kubernetes", k=5)
    assert [c.id for c, _ in hits] == ["a"]
    assert hits[0][1] == 0.0


def test_bm25_returns_nothing_when_no_chunk_shares_a_term():
    chunks = [_chunk("a", "kubernetes platform"), _chunk("b", "angular frontend")]
    assert Bm25Index(chunks).search("terraform", k=5) == []


def test_dense_returns_nearest_first():
    chunks = [_chunk("a", "x"), _chunk("b", "y"), _chunk("c", "z")]
    vectors = np.array([[1.0, 0.0], [0.0, 1.0], [0.7071, 0.7071]], dtype=np.float32)
    hits = DenseIndex(chunks, vectors).search(np.array([1.0, 0.0], dtype=np.float32), k=3)
    assert [c.id for c, _ in hits] == ["a", "c", "b"]
    assert hits[0][1] > hits[1][1] > hits[2][1]


def test_dense_respects_k():
    chunks = [_chunk("a", "x"), _chunk("b", "y")]
    vectors = np.array([[1.0, 0.0], [0.0, 1.0]], dtype=np.float32)
    assert len(DenseIndex(chunks, vectors).search(np.array([1.0, 0.0], dtype=np.float32), k=1)) == 1


def test_query_terms_drop_function_words_but_keep_codes():
    assert query_terms("Wie heeft het AZ-900 certificaat?") == ["az-900", "certificaat"]


def test_bm25_finds_an_exact_code_a_long_document_would_otherwise_bury():
    chunks = [
        _chunk("long", " ".join(["wie heeft het dat de een en van is"] * 60)),
        _chunk("cv", "Certificaten: AZ-900 Azure Fundamentals"),
    ]
    hits = Bm25Index(chunks).search("Wie heeft het AZ-900 certificaat?", k=2)
    assert hits[0][0].id == "cv"


def test_bm25_returns_nothing_for_an_all_stopword_query():
    assert Bm25Index([_chunk("a", "iets")]).search("wie is dat?", k=5) == []
