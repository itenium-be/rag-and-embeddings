import numpy as np
import pytest

from rag.app import warm_models


class Recorder:
    def __init__(self, fail: bool = False) -> None:
        self.embedded: list[str] = []
        self.scored: list[str] = []
        self.fail = fail

    def embed_query(self, text: str):
        if self.fail:
            raise RuntimeError("no weights on disk")
        self.embedded.append(text)
        return np.zeros(2, dtype=np.float32)

    def score(self, query: str, texts: list[str]) -> list[float]:
        self.scored.append(query)
        return [0.0] * len(texts)


class FakeEngine:
    def __init__(self, recorder: Recorder) -> None:
        self.embed_query = recorder.embed_query
        self.reranker = recorder


def test_warming_loads_both_models():
    recorder = Recorder()
    warm_models(FakeEngine(recorder))
    assert recorder.embedded
    assert recorder.scored


def test_warming_reports_when_the_models_are_ready(caplog):
    with caplog.at_level("INFO", logger="rag.app"):
        warm_models(FakeEngine(Recorder()))
    assert "ready" in caplog.text


def test_a_model_that_will_not_load_is_logged_not_raised(caplog):
    with caplog.at_level("INFO", logger="rag.app"):
        warm_models(FakeEngine(Recorder(fail=True)))
    assert "no weights on disk" in caplog.text
