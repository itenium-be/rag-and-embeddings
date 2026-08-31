from pathlib import Path

from rag.ingest import ingest_corpus, person_name, swap_name

SAMPLE = Path(__file__).resolve().parents[1] / "sample"


def test_ingests_every_source_type():
    chunks = ingest_corpus(SAMPLE)
    types = {c.source_type for c in chunks}
    assert types == {"policy", "cv", "assignment", "credit", "aggregate"}


def test_person_name_survives_the_real_filename_shapes():
    assert person_name("Itenium - CV Alexander Ryckeboer") == "Alexander Ryckeboer"
    assert person_name("Itenium - CV Bernard Giorgino (FA)") == "Bernard Giorgino"
    assert person_name("Itenium - CV Bert Maes - Business Architect ") == "Bert Maes"
    assert person_name("Itenium - CV Bert Vermorgen - ENG") == "Bert Vermorgen"
    assert (
        person_name("Itenium - CV Bram De Plekker - .NET Angular Cloud Developer - updated")
        == "Bram De Plekker"
    )


def test_swap_name_turns_the_export_order_around():
    assert swap_name("Peeters, Dries") == "Dries Peeters"
    assert swap_name("De Plekker, Bram") == "Bram De Plekker"
    assert swap_name("Madonna") == "Madonna"


def test_assignment_chunks_drop_personal_data():
    chunks = [c for c in ingest_corpus(SAMPLE) if c.source_type == "assignment"]
    joined = "\n".join(c.text for c in chunks)
    # Assert on the field labels, not on bare values: "Antwerpen" is also a substring
    # of "UAntwerpen" in the College column, and "2000" is a zip code, a year and part
    # of "EUR 2000". A dropped column is one whose label never appears.
    for label in (
        "Birth Date", "Gender", "City", "State", "Zip Code", "Work Email", "LinkedIn URL",
    ):
        assert f"{label}:" not in joined
    # Two values that cannot collide with anything legitimate.
    for leaked in ("1990-04-11", "ana.meeus@example.be"):
        assert leaked not in joined
    assert "Klant: RetailCo" in joined


def test_credit_rows_are_one_chunk_each():
    chunks = [c for c in ingest_corpus(SAMPLE) if c.source_type == "credit"]
    assert len(chunks) == 28
    assert all(c.title for c in chunks)


def test_no_credit_chunk_contains_a_balance():
    """Question 5's whole point: the answer is in no retrievable chunk."""
    chunks = [c for c in ingest_corpus(SAMPLE) if c.source_type == "credit"]
    assert all("450" not in c.text for c in chunks)


def test_aggregate_chunk_states_the_summed_balance():
    chunks = [c for c in ingest_corpus(SAMPLE) if c.source_type == "aggregate"]
    dries = next(c for c in chunks if c.title == "Dries Peeters")
    assert "450" in dries.text


def test_aggregates_cover_every_person_in_the_ledger():
    chunks = ingest_corpus(SAMPLE)
    ledger_people = {c.title for c in chunks if c.source_type == "credit"}
    summary_people = {c.title for c in chunks if c.source_type == "aggregate"}
    assert ledger_people == summary_people


def test_cv_chunks_carry_the_person_name_as_title():
    titles = {c.title for c in ingest_corpus(SAMPLE) if c.source_type == "cv"}
    assert {"Dries Peeters", "Bram Claes"} <= titles


def test_policy_chunks_carry_a_heading_path():
    locations = [c.location for c in ingest_corpus(SAMPLE) if c.source_type == "policy"]
    assert any("Opleidingsbudget" in loc for loc in locations)


def test_chunk_ids_are_unique():
    chunks = ingest_corpus(SAMPLE)
    assert len({c.id for c in chunks}) == len(chunks)
