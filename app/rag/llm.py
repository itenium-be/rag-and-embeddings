"""The only part of the pipeline that touches the network, and it is cached.

Keying on (system, prompt) rather than on (question, config) is deliberate: two configs
that produce the same prompt should share a cache entry, and a prompt edit should not
silently reuse an answer written for the previous wording.
"""

from __future__ import annotations

import hashlib
import json
import logging
import shutil
import subprocess
import time
from pathlib import Path
from typing import Protocol

log = logging.getLogger(__name__)

MODEL = "claude-opus-5"
MAX_TOKENS = 2048
# A cold CLI call on a long prompt is slow; a demo cache miss must not look like a hang.
CLI_TIMEOUT = 180
# Step -1 sends the whole corpus. Measured at 16s, but one slow call costs the demo.
LONG_CLI_TIMEOUT = 600
# Linux caps a single argv string at MAX_ARG_STRLEN, 32 pages. Past it, execve fails with
# E2BIG, so a prompt that big has to reach the CLI on stdin instead.
ARGV_LIMIT = 100_000


class NoAnswerAvailable(RuntimeError):
    """Cache miss with no way to reach the model."""


class LLM(Protocol):
    def complete(self, system: str, prompt: str) -> str: ...


class AnthropicLLM:
    """Zero-arg client: it resolves the OAuth profile written by `ant auth login`."""

    def __init__(self) -> None:
        from anthropic import Anthropic

        self._client = Anthropic()

    def complete(self, system: str, prompt: str) -> str:
        message = self._client.messages.create(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            system=system,
            messages=[{"role": "user", "content": prompt}],
        )
        return "".join(b.text for b in message.content if b.type == "text")


class ClaudeCliLLM:
    """Runs prompts through the Claude Code CLI, which bills a Claude subscription.

    The Messages API draws on org API credit, which is a different balance from a
    subscription and has to be topped up separately. This path needs only `claude` on
    PATH and an interactive login, so the demo runs on the same plan the presenter
    already pays for.
    """

    def __init__(self, runner=subprocess.run, model: str = MODEL) -> None:
        self._run = runner
        self._model = model

    def complete(self, system: str, prompt: str) -> str:
        return self.complete_with_usage(system, prompt)[0]

    def complete_with_usage(self, system: str, prompt: str) -> tuple[str, dict]:
        piped = len(prompt.encode("utf-8")) > ARGV_LIMIT
        argv = ["claude", "-p"]
        if not piped:
            argv.append(prompt)
        argv += [
            "--system-prompt", system,
            # An agent with tools would go exploring; this is a single completion.
            "--allowed-tools", "",
            "--model", self._model,
            # Carries the token counts and the price of the call, which is the whole
            # argument step -1 exists to make.
            "--output-format", "json",
        ]
        completed = self._run(
            argv,
            capture_output=True,
            text=True,
            input=prompt if piped else None,
            timeout=LONG_CLI_TIMEOUT if piped else CLI_TIMEOUT,
        )
        if completed.returncode != 0:
            raise RuntimeError(
                f"claude exited {completed.returncode}: {completed.stderr.strip()[:300]}"
            )
        return parse_cli_reply(completed.stdout)


def parse_cli_reply(stdout: str) -> tuple[str, dict]:
    """Split `--output-format json` into the answer and what the call cost.

    Anything unparseable is the answer with no usage: the strip is commentary on the
    demo, and losing an answer to a reporting field would be a bad trade.
    """
    try:
        payload = json.loads(stdout)
        usage = payload["usage"]
    except (ValueError, KeyError, TypeError):
        return stdout.strip(), {}

    cache_read = usage.get("cache_read_input_tokens", 0)
    cache_creation = usage.get("cache_creation_input_tokens", 0)
    return payload.get("result", "").strip(), {
        # The CLI bills cached input on its own lines; the size of the prompt is the sum.
        "input_tokens": usage.get("input_tokens", 0) + cache_read + cache_creation,
        "cache_read_tokens": cache_read,
        "cache_creation_tokens": cache_creation,
        "output_tokens": usage.get("output_tokens", 0),
        "cost_usd": payload.get("total_cost_usd"),
        "duration_ms": payload.get("duration_ms"),
    }


def cache_key(system: str, prompt: str) -> str:
    payload = json.dumps({"system": system, "prompt": prompt}, sort_keys=True)
    return hashlib.sha256(payload.encode()).hexdigest()[:32]


class CachedLLM:
    def __init__(self, inner: LLM | None, cache_dir: Path) -> None:
        self._inner = inner
        self._dir = Path(cache_dir)
        self._dir.mkdir(parents=True, exist_ok=True)

    def _path(self, system: str, prompt: str) -> Path:
        return self._dir / f"{cache_key(system, prompt)}.json"

    def _read(self, system: str, prompt: str) -> tuple[str, dict] | None:
        path = self._path(system, prompt)
        if not path.is_file():
            return None
        entry = json.loads(path.read_text(encoding="utf-8"))
        # Entries warmed before the cost strip existed carry no usage.
        return entry["response"], entry.get("usage", {})

    def _call_inner(self, system: str, prompt: str) -> tuple[str, dict]:
        if hasattr(self._inner, "complete_with_usage"):
            return self._inner.complete_with_usage(system, prompt)
        return self._inner.complete(system, prompt), {}

    def complete(
        self, system: str, prompt: str, *, fallback_to: str | None = None, label: str = "llm"
    ) -> str:
        return self.complete_with_usage(
            system, prompt, fallback_to=fallback_to, label=label
        )[0]

    def complete_with_usage(
        self, system: str, prompt: str, *, fallback_to: str | None = None, label: str = "llm"
    ) -> tuple[str, dict]:
        cached = self._read(system, prompt)
        if cached is not None:
            log.info("   %-9s %s · cache hit", "llm", label)
            return cached

        if self._inner is None:
            raise NoAnswerAvailable(
                "No cached answer and no credential. Run scripts/warm_cache.py, "
                "or `ant auth login` to enable live calls."
            )

        started = time.perf_counter()
        try:
            response, usage = self._call_inner(system, prompt)
        except Exception:
            # On stage, a stale answer beats a stack trace.
            if fallback_to is not None:
                stale = self._read(system, fallback_to)
                if stale is not None:
                    log.info("   %-9s %s · cache miss, the call failed — serving a stale answer", "llm", label)
                    return stale
            raise
        log.info("   %-9s %s · cache miss → %.1fs", "llm", label, time.perf_counter() - started)

        self._path(system, prompt).write_text(
            json.dumps(
                {"system": system, "prompt": prompt, "response": response, "usage": usage}
            ),
            encoding="utf-8",
        )
        return response, usage


def build_llm(cache_dir: Path) -> CachedLLM:
    """Prefer the CLI: it runs on a subscription, where the API needs org credit."""
    inner: LLM | None = None
    if shutil.which("claude"):
        inner = ClaudeCliLLM()
    else:
        try:
            inner = AnthropicLLM()
        except Exception:
            inner = None
    return CachedLLM(inner, cache_dir)
