"""The CLI transport: how a prompt reaches `claude`, and what it reports back."""

from __future__ import annotations

import json

import pytest

from rag.llm import ARGV_LIMIT, CLI_TIMEOUT, LONG_CLI_TIMEOUT, CachedLLM, ClaudeCliLLM


def cli_json(result="answer", input_tokens=10, cache_read=0, cost=0.01, duration_ms=1200):
    return json.dumps(
        {
            "result": result,
            "total_cost_usd": cost,
            "duration_ms": duration_ms,
            "usage": {
                "input_tokens": input_tokens,
                "cache_read_input_tokens": cache_read,
                "cache_creation_input_tokens": 0,
                "output_tokens": 5,
            },
        }
    )


class FakeCompleted:
    def __init__(self, returncode=0, stdout=None, stderr=""):
        self.returncode = returncode
        self.stdout = cli_json() if stdout is None else stdout
        self.stderr = stderr


class Recorder:
    def __init__(self, stdout=None):
        self.stdout = stdout
        self.argv = None
        self.kwargs = None

    def __call__(self, argv, **kwargs):
        self.argv = argv
        self.kwargs = kwargs
        return FakeCompleted(stdout=self.stdout)


def test_a_short_prompt_still_goes_through_argv():
    runner = Recorder()
    ClaudeCliLLM(runner=runner).complete("sys", "prompt")
    assert runner.argv[:3] == ["claude", "-p", "prompt"]
    assert runner.kwargs.get("input") is None


def test_a_prompt_past_the_argv_limit_is_piped_on_stdin():
    """Linux caps one argv string at 128 KB, so the corpus cannot be an argument."""
    runner = Recorder()
    corpus = "x" * (ARGV_LIMIT + 1)
    ClaudeCliLLM(runner=runner).complete("sys", corpus)
    assert runner.kwargs["input"] == corpus
    assert corpus not in runner.argv
    assert runner.argv[runner.argv.index("-p") + 1].startswith("--")


def test_the_limit_counts_bytes_not_characters():
    """`é` is two bytes, and it is the kernel that does the counting."""
    runner = Recorder()
    ClaudeCliLLM(runner=runner).complete("sys", "é" * (ARGV_LIMIT // 2 + 1))
    assert runner.kwargs.get("input") is not None


def test_a_piped_prompt_gets_the_longer_timeout():
    runner = Recorder()
    llm = ClaudeCliLLM(runner=runner)
    llm.complete("sys", "short")
    assert runner.kwargs["timeout"] == CLI_TIMEOUT
    llm.complete("sys", "x" * (ARGV_LIMIT + 1))
    assert runner.kwargs["timeout"] == LONG_CLI_TIMEOUT


def test_the_system_prompt_stays_an_argument_when_the_prompt_is_piped():
    runner = Recorder()
    ClaudeCliLLM(runner=runner).complete("sys", "x" * (ARGV_LIMIT + 1))
    assert runner.argv[runner.argv.index("--system-prompt") + 1] == "sys"
    assert runner.argv[runner.argv.index("--allowed-tools") + 1] == ""


def test_usage_totals_every_kind_of_input_token():
    """The CLI bills cached input separately; the room wants the size of the prompt."""
    runner = Recorder(stdout=cli_json(input_tokens=2, cache_read=262_000, cost=0.13))
    _, usage = ClaudeCliLLM(runner=runner).complete_with_usage("sys", "prompt")
    assert usage["input_tokens"] == 262_002
    assert usage["cache_read_tokens"] == 262_000
    assert usage["cost_usd"] == 0.13


def test_a_reply_that_is_not_json_is_still_an_answer():
    """Never lose an answer to a reporting field: the strip is commentary, the answer is not."""
    runner = Recorder(stdout="plain text reply")
    text, usage = ClaudeCliLLM(runner=runner).complete_with_usage("sys", "prompt")
    assert text == "plain text reply"
    assert usage == {}


def test_the_cli_still_raises_with_stderr_when_it_fails():
    def runner(argv, **kwargs):
        return FakeCompleted(returncode=1, stdout="", stderr="not logged in")

    with pytest.raises(RuntimeError, match="not logged in"):
        ClaudeCliLLM(runner=runner).complete("sys", "prompt")


class UsageLLM:
    def __init__(self):
        self.calls = 0

    def complete_with_usage(self, system, prompt):
        self.calls += 1
        return "answer", {"input_tokens": 262_000, "cost_usd": 1.31}


def test_usage_is_cached_beside_the_answer(tmp_path):
    """A warmed answer has to show what it cost, or the cost strip is blank on stage."""
    inner = UsageLLM()
    CachedLLM(inner, tmp_path).complete_with_usage("sys", "prompt")
    text, usage = CachedLLM(inner, tmp_path).complete_with_usage("sys", "prompt")
    assert inner.calls == 1
    assert text == "answer"
    assert usage["cost_usd"] == 1.31


class PlainLLM:
    def complete(self, system, prompt):
        return "answer"


def test_an_llm_that_reports_no_usage_still_answers(tmp_path):
    text, usage = CachedLLM(PlainLLM(), tmp_path).complete_with_usage("sys", "prompt")
    assert text == "answer"
    assert usage == {}


def test_an_entry_cached_before_usage_existed_still_reads(tmp_path):
    (tmp_path / "x.json").write_text("{}")
    CachedLLM(PlainLLM(), tmp_path).complete("sys", "prompt")
    _, usage = CachedLLM(PlainLLM(), tmp_path).complete_with_usage("sys", "prompt")
    assert usage == {}
