# Step -1 · Context — the long-context baseline

Adds a `-1 · Context` tab to the demo app. It answers a question by putting the entire
corpus in the prompt, with no retrieval of any kind, and shows what that costs.

This is [When not to reach for this](../../../notes/When-Not-To-RAG.md) made runnable:

> The pragmatic move: try long context first as a quality baseline. If dumping everything
> in the prompt answers your five questions and RAG does not, you have learned something
> important about your retrieval before building any of it.

The tab exists to *test* that claim on this corpus, not to illustrate it. Measured, it
half survives: three of the five questions green, one partial, one failed.

| Question    | Step -1  | Best RAG step |
| ----------- | -------- | ------------- |
| ai-tools    | pass     | 1             |
| fietslease  | pass     | 1             |
| az-900      | pass     | 3             |
| laptoplader | partial  | 4             |
| creditsaldo | fail     | 6             |

Two of those results are worth more than the score.

**AZ-900 passes while contradicting itself.** The answer opens "de bronnen bevatten geen
enkele vermelding van een AZ-900-certificaat" and then lists all four holders, correctly
excluding the one whose CV shows only an exam-prep course. The critic scores facts, the
facts are all present, and the first sentence is false. Retrieving five chunks never
produces that failure.

**The ledger question fails with all 946 rows in the prompt.** Not because it cannot see
them — because it declines to add them up: "optellen van alle boekingen op zijn naam
levert een getal op, maar de bronnen zeggen niet dat dat het actuele saldo is". A bigger
context window is not an aggregation engine either. Only step 6 is.

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

Measured, not estimated: `2151 chunks · 501k tokens in · $4.93 · 14.5s`.

Half a million tokens, not the 250k a `chars / 4` estimate predicts — Dutch policy text
and Flemish proper nouns tokenize at roughly two characters each. The cost is high for
the same reason plus cache *creation*, billed at 1.25x: a repeat inside the window reads
the corpus back at a tenth of that.

The token count is what the CLI bills, which includes its own system prompt. The strip
says *as billed* rather than claiming to be pure corpus, and only calls a call cached
when the cache read is most of the input — the CLI always cache-reads its own preamble,
so a few thousand cached tokens says nothing about the corpus.

## Citations

Chunks stay numbered across the whole corpus and `extract_citations` runs against the full
list, so the tab can show a Sources box. Long context can cite; the room will ask.

## Verdicts

Each question gains a `-1` key in its `steps` map, measured against the real corpus like
every other prediction in that file. The scoreboard renders it with no change: `verdict()`
already reads `q.steps[step]`.

Step -1 is judged on its **answer**, never on what it retrieved: everything is retrieved
by construction, so `includes` and `everyone` would pass on any question at all. It is
scored the way `everyone` scores retrieval — every checklist item is a pass, most of them
is `partial`, fewer is a failure.

`demo_at` skips it. Step -1 demonstrates no technique; it is what the techniques are
measured against.

The live answer critic runs as it does at every other step.

## Testing

Unit, no network, no models:

- the corpus is sorted, contiguous per document, and contains no aggregate chunk
- a prompt past the argv limit takes the stdin path; a short one does not
- usage JSON parses, and a missing field does not take the answer down with it
- `/api/context` returns the documented shape

Then one measured pass over the five questions to fill the `-1` column, which the slow
scoreboard asserts from then on: 35 assertions, up from 30.

## Risks

- **A live miss on stage** costs the measured 12-16s. `warm_cache.py` covers the prepared five.
- **Rebuilding the index changes every step -1 cache key**, because the corpus is the
  prompt. The README already documents the same trap for `index-real`; it gains a line.
- **~5 MB of new cache files.** `data/` is gitignored in full.
