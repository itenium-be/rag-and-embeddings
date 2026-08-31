import pytest

from rag.llm import CachedLLM, NoAnswerAvailable


class CountingLLM:
    def __init__(self, reply: str = "answer") -> None:
        self.reply = reply
        self.calls = 0

    def complete(self, system: str, prompt: str) -> str:
        self.calls += 1
        return self.reply


def test_second_identical_call_is_served_from_cache(tmp_path):
    inner = CountingLLM()
    llm = CachedLLM(inner, tmp_path)
    assert llm.complete("sys", "prompt") == "answer"
    assert llm.complete("sys", "prompt") == "answer"
    assert inner.calls == 1


def test_different_prompt_is_a_different_entry(tmp_path):
    inner = CountingLLM()
    llm = CachedLLM(inner, tmp_path)
    llm.complete("sys", "one")
    llm.complete("sys", "two")
    assert inner.calls == 2


def test_cache_survives_a_new_process(tmp_path):
    CachedLLM(CountingLLM(), tmp_path).complete("sys", "prompt")
    inner = CountingLLM()
    assert CachedLLM(inner, tmp_path).complete("sys", "prompt") == "answer"
    assert inner.calls == 0


def test_offline_mode_serves_cache_and_refuses_a_miss(tmp_path):
    CachedLLM(CountingLLM(), tmp_path).complete("sys", "hit")
    offline = CachedLLM(None, tmp_path)
    assert offline.complete("sys", "hit") == "answer"
    with pytest.raises(NoAnswerAvailable):
        offline.complete("sys", "miss")


def test_upstream_failure_falls_back_to_any_cached_answer(tmp_path):
    class Broken:
        def complete(self, system: str, prompt: str) -> str:
            raise RuntimeError("api down")

    CachedLLM(CountingLLM("earlier"), tmp_path).complete("sys", "hit")
    llm = CachedLLM(Broken(), tmp_path)
    assert llm.complete("sys", "miss", fallback_to="hit") == "earlier"
