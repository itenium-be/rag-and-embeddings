"""The only part of the pipeline that touches the network, and it is cached.

Keying on (system, prompt) rather than on (question, config) is deliberate: two configs
that produce the same prompt should share a cache entry, and a prompt edit should not
silently reuse an answer written for the previous wording.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Protocol

MODEL = "claude-opus-5"
MAX_TOKENS = 2048


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

    def _read(self, system: str, prompt: str) -> str | None:
        path = self._path(system, prompt)
        if not path.is_file():
            return None
        return json.loads(path.read_text(encoding="utf-8"))["response"]

    def complete(self, system: str, prompt: str, *, fallback_to: str | None = None) -> str:
        cached = self._read(system, prompt)
        if cached is not None:
            return cached

        if self._inner is None:
            raise NoAnswerAvailable(
                "No cached answer and no credential. Run scripts/warm_cache.py, "
                "or `ant auth login` to enable live calls."
            )

        try:
            response = self._inner.complete(system, prompt)
        except Exception:
            # On stage, a stale answer beats a stack trace.
            if fallback_to is not None:
                stale = self._read(system, fallback_to)
                if stale is not None:
                    return stale
            raise

        self._path(system, prompt).write_text(
            json.dumps({"system": system, "prompt": prompt, "response": response}),
            encoding="utf-8",
        )
        return response


def build_llm(cache_dir: Path) -> CachedLLM:
    try:
        inner: LLM | None = AnthropicLLM()
    except Exception:
        inner = None
    return CachedLLM(inner, cache_dir)
