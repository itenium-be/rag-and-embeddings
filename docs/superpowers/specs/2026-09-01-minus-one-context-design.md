# Step -1 · Context — the long-context baseline

Adds a `-1 · Context` tab to the demo app. It answers a question by putting the entire
corpus in the prompt, with no retrieval of any kind, and shows what that costs.

This is [When not to reach for this](../../../notes/When-Not-To-RAG.md) made runnable:

> The pragmatic move: try long context first as a quality baseline. If dumping everything
> in the prompt answers your five questions and RAG does not, you have learned something
> important about your retrieval before building any of it.

The tab exists to *test* that claim on this corpus, not to illustrate it. The first
measurement already contradicts the optimistic reading: on AZ-900 long context opens with
a false refusal, then names three of the four holders in the next sentence — worse than
step 3, on the question step 3 exists to fix.

## What goes in the context

The 2151 chunks of `chunks.jsonl` minus the 43 `aggregate` chunks, sorted by
`(source, location)` so each document reads contiguously, numbered `[n]` over the whole
corpus. 1.02 MB.

Chunks rather than the source documents, for three reasons:

1. The only variable between step -1 and step 1 is then the retrieval step. Re-extracting
   from `data/raw/` would let any difference be blamed on different PDF parsing.
2. `data/raw/` is gitignored and `sample/` has no raw documents, so a document path needs
   two ingest branches, and the sample demo would stop reproducing the real one.
3. Sorting by `(source, location)` reconstitutes each document anyway.

Aggregates are excluded because they *are* step 6's answer precomputed. Without them the
`creditsaldo` question forces long context to sum 946 ledger rows itself, which is the
retrieval-versus-structure argument tested from the other side.

## Modules

| Module                  | Change                                                                                                                  |
| ----------------------- | ----------------------------------------------------------------------------------------------------------------------- |
| `rag/longcontext.py`    | New. `build_corpus(chunks) -> str` and `answer(llm, question, corpus) -> str`. Pure; no network, no models, no FastAPI. |
| `rag/llm.py`            | `ClaudeCliLLM` pipes the prompt on stdin past the argv limit; long calls report usage.                                   |
| `web/server.py`         | `POST /api/context` → answer, citations, critic verdict, usage. Corpus built once at startup.                            |
| `web/static/index.html` | `-1 · Context` button, its own main, ask box, answer, critic, cost strip.                                               |
| `questions.yaml`        | A `-1` key per question, measured.                                                                                       |
| `scripts/warm_cache.py` | Warms step -1 alongside the six wizard steps.                                                                            |

### Transport

A 1 MB prompt cannot go through `-p`: Linux caps a single argv string at `MAX_ARG_STRLEN`,
128 KB, and the call fails with `E2BIG`. Past that size the prompt is piped to the CLI on
stdin instead, which `claude -p` reads with no prompt argument at all.

`CachedLLM` keys on `(system, prompt)`, so transport does not enter the key and the 241
already-warmed entries stay valid.

Long-context calls add `--output-format json`, which reports `usage.input_tokens`,
`total_cost_usd` and `duration_ms` — real numbers for the cost strip rather than a
`chars / 4` guess. They get their own 600s timeout: `CLI_TIMEOUT` is 180s, which is ten
times the measured 16s but not a margin worth betting a talk on.

## Cost strip

`2151 chunks · 262k in · 16.4s · $1.31`, and on a repeat inside the CLI's cache window
`cache read 262k · $0.13` — [Cost and Caching](../../../notes/Cost-And-Caching.md)
demonstrating itself.

The token count is what the CLI bills, which includes roughly 22k tokens of Claude Code's
own system prompt. The strip is labelled *as billed* rather than presented as pure corpus.

## Citations

Chunks stay numbered across the whole corpus and `extract_citations` runs against the full
list, so the tab can show a Sources box. Long context can cite; the room will ask.

## Verdicts

Each question gains a `-1` key in its `steps` map, measured against the real corpus like
every other prediction in that file. The scoreboard renders it with no change: `verdict()`
already reads `q.steps[step]`.

The live answer critic runs as it does at every other step.

## Testing

Unit, no network, no models:

- the corpus is sorted, contiguous per document, and contains no aggregate chunk
- a prompt past the argv limit takes the stdin path; a short one does not
- usage JSON parses, and a missing field does not take the answer down with it
- `/api/context` returns the documented shape

Then one measured pass over the five questions to fill the `-1` column.

## Risks

- **A live miss on stage** costs the measured ~16s. `warm_cache.py` covers the prepared five.
- **Rebuilding the index changes every step -1 cache key**, because the corpus is the
  prompt. The README already documents the same trap for `index-real`; it gains a line.
- **~5 MB of new cache files.** `data/` is gitignored in full.
