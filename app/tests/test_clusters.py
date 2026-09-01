import numpy as np

from rag.models import Chunk
from web.clusters import cluster_ellipses, group_of


def chunk(source_type: str, title: str = "t") -> Chunk:
    return Chunk(id="i", text="x", source="s", source_type=source_type, title=title, location="l")


def test_cvs_and_credits_are_named_after_their_source_type():
    assert group_of(chunk("cv", "Bram Claes")) == "CVs"
    assert group_of(chunk("credit", "Bram Claes")) == "Credits"


def test_assignments_join_the_credits_they_are_booked_against():
    assert group_of(chunk("assignment", "Bram Claes")) == "Credits"


def test_car_and_rental_policies_split_off_from_the_rest_of_the_policies():
    assert group_of(chunk("policy", "Car Policy - NEW - 14052025")) == "Car Policy"
    assert group_of(chunk("policy", "General-Conditions-of-Rental-per-16-06-2022")) == "Car Policy"
    assert group_of(chunk("policy", "Arbeidsreglement")) == "HR Policy"


def test_ellipse_sits_on_the_blob_and_ignores_one_stray_point():
    chunks = [chunk("cv") for _ in range(10)]
    blob = [[x / 10, y / 10] for x in range(-4, 5, 2) for y in (-2, 2)][:9]
    projection = np.array(blob + [[100.0, 100.0]])

    (cvs,) = cluster_ellipses(chunks, projection, min_share=0.0)

    assert cvs["label"] == "CVs"
    assert cvs["count"] == 10
    assert abs(cvs["x"]) < 1 and abs(cvs["y"]) < 1
    assert cvs["rx"] < 2 and cvs["ry"] < 2


def test_groups_smaller_than_the_minimum_share_get_no_circle():
    chunks = [chunk("cv") for _ in range(19)] + [chunk("aggregate")]
    projection = np.zeros((20, 2))

    labels = [c["label"] for c in cluster_ellipses(chunks, projection, min_share=0.1)]

    assert labels == ["CVs"]
