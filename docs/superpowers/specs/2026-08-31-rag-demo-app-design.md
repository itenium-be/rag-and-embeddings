# RAG demo app — design

The live demo for the [RAG & Embeddings session](../../../notes/Session-Outline.md). One
corpus, five questions, a six-step wizard that mirrors the talk. Four questions are fixed by
retrieval techniques. The fifth is not fixed by any of them — it is fixed by computing the
answer at ingest time, which is the argument for the next session made concrete.

## Purpose

The [session outline](../../../notes/Session-Outline.md) is built around a scoreboard: naive
vector RAG answers question 1, fails questions 2–5, and each technique introduced in part 4
fixes exactly one. The app is what the room watches while that happens. It has to make the
difference between "before" and "after" visible on a projector, and it has to be impossible
to break in front of an audience.

### The questions

Every one is a question a consultant in the room would actually type. The outline's original
set was written from the back office's point of view — "who has AZ-204", "who is free in
October" — which are staffing questions the audience does not ask.

| # | Question | Naive RAG does | Fixed by |
| --- | --- | --- | --- |
| 1 | Hoeveel opleidingsbudget heb ik per jaar? | ✅ answers it | — the baseline |
| 2 | Hoe geef ik mijn kilometerstand door aan XXimo? | returns the general kilometervergoeding policy | hybrid search |
| 3 | Wie kan me helpen met Kubernetes? | five CVs that mention it once | reranking |
| 4 | Mag ik mijn opleidingsbudget gebruiken voor een conferentie in Lissabon? | lands on the travel-expenses document | query rewriting |
| 5 | Hoeveel credits heb ik nog? | invents a number | ❌ not by retrieval — see step 6 |

Question 2 is doing double duty. `XXimo`, `Renta Norm` and `SD Worx` are internal jargon the
embedding model has never seen, so meaning-search is blind to them while keyword search is
perfect at them. That is part 1's "the map is *learned*, so it is poor at your vocabulary"
point, demonstrated rather than asserted.

Question 5 is a ledger sum: 946 signed rows across 43 people, and the balance appears in no
chunk. Step 6 fixes it by precomputing one summary chunk per consultant at ingest time — not
a retrieval technique, and saying so out loud is the point. *"I did not improve retrieval. I
added structure."*

## Scope

**In:** ingestion of policy PDFs, CVs and a BambooHR export; local embeddings; dense, BM25,
RRF, rerank and query-rewrite retrieval; answer generation with citations; a wizard UI over
all of it; a 2D embedding map; a test that asserts the scoreboard.

**Out:** authentication, per-user access control (that is session three's closing slide —
described, not built), pgvector or any external vector store, a live BambooHR integration,
deployment, and the slides themselves. Slides come after the app, so the screenshots are of
real failures rather than invented ones.

## Data

Three sources, all dropped by hand into `app/data/raw/`. No credentials are handled anywhere
in this project.

| Source | Where | Format | Chunking | Role |
| --- | --- | --- | --- | --- |
| Policies — AI policy, approved AI tools, arbeidsreglement, car policy, opleidingsplan, kilometervergoeding, XXimo, health insurance, HR & fleet FAQ (24 files) | `data/raw/pdfs/` | PDF, DOCX, TXT | ~800 chars, 100 overlap, heading path in metadata | Questions 1, 2 and 4 |
| Consultant CVs (37) | `data/raw/cvs/` | PDF, DOCX | Same split, name parsed from the filename | Question 3 |
| Assignment history (57 rows, 43 people) | `data/raw/bamboo/consultants.csv` | CSV | **One row = one chunk**, rendered as fields | Context; the near-identical-blob demonstration |
| Credits ledger (946 rows, 43 people) | `data/raw/bamboo/credits.csv` | CSV | One booking = one chunk | Question 5 — the failure |
| Credit balances | derived | — | One summary chunk per consultant, **computed at ingest** | Question 5 — the fix, at step 6 |

`.xlsx` files in the drop (timesheets, expense templates) are skipped: they are forms, not
prose.

The BambooHR chunking is deliberately the wrong thing to do. Records rendered as
near-identical text blobs sit on top of each other in vector space, which is precisely the
demonstration the [demo data note](../../../notes/Demo-Data.md) asks for: retrieval over
chunks is not a substitute for structure.

### Data protection

The corpus is real internal employee data, used internally. Two rules hold anyway:

**Never indexed.** Compensation, performance reviews and goals, and anything touching leave
*reasons*. The five questions do not need them, and leave reasons are health data.

The `consultants.csv` export also carries `Birth Date`, `Gender`, `City`, `State`,
`Zip Code`, `Work Email` and `LinkedIn URL`. Date of birth and home address are on the
leave-out list; none of the five questions needs any of them. Ingestion drops those columns,
so they never reach the vector store even though they are present in the file on disk.

**Never committed.** All of `app/data/` is gitignored — `raw/` obviously, but also `index/`
and `cache/`:

- `chunks.jsonl` is CV and BambooHR text in plaintext.
- `embeddings.npy` is not a safe stand-in for it; embedding inversion recovers approximate
  source text.
- Cached answers quote retrieved chunks back verbatim.

### Sample corpus

`app/sample/` is committed and contains ~15 invented consultants and 2 invented policy
documents, hand-written so that all five questions fail and get fixed exactly as the real
corpus does. It makes a fresh clone runnable, and it is the fixture the retrieval tests run
against. Real data in `app/data/raw/` shadows it when present.

## Architecture

```
app/
  pyproject.toml
  data/                 gitignored in full
    raw/                PDFs, CVs, BambooHR export — dropped by hand
    index/              chunks.jsonl, embeddings.npy, projection.npy
    cache/              LLM responses keyed by (question, config)
  sample/               committed synthetic corpus
  rag/
    chunks.py           Chunk, Scored, Citation, Result
    ingest.py           parse -> chunk -> chunks.jsonl
    embed.py            sentence-transformers wrapper
    index.py            DenseIndex (numpy), Bm25Index
    retrieve.py         dense, bm25, rrf, rerank
    rewrite.py          step-back / decompose
    generate.py         answer + citations
    llm.py              LLM protocol, Anthropic impl, disk cache
    pipeline.py         Config -> run(question, config) -> Result
  web/
    server.py           FastAPI
    static/index.html   one page, no build step
  scripts/
    build_index.py      ingest + embed + project
    warm_cache.py       every question x every wizard step
  tests/
  questions.yaml        the five questions and their expected verdict per step
```

`rag/retrieve.py` is the module that goes on a slide. The outline promises the whole pipeline
in under fifty lines; keep it that readable and let the ceremony live elsewhere.

### The pipeline

One frozen config drives every variation. A wizard step is a preset.

```python
@dataclass(frozen=True)
class Config:
    dense: bool = True
    bm25: bool = False
    rerank: bool = False
    rewrite: bool = False
    citations: bool = False
    top_k: int = 50   # retrieve wide
    top_n: int = 5    # keep few
```

| Step | Preset | Flips |
| --- | --- | --- |
| 0 | — the embedding map | — |
| 1 | `dense` | baseline: Q1 green, Q2–5 red |
| 2 | `+ bm25` | Q2 |
| 3 | `+ rerank` | Q3 |
| 4 | `+ rewrite` | Q4 |
| 5 | `+ citations` | — provenance, no scoreboard change |
| 6 | `+ aggregates` | Q5 — and not by retrieval |

Step 6 does not add a technique. It lets the precomputed balance chunks into retrieval; they
are in the index from the start and hidden until then. Everything the first five steps do is
a way of finding a passage that resembles the question. Step 6 works because someone did the
arithmetic before the vectors existed.

`run(question, config) -> Result` returns every candidate with **its rank at each stage**, not
just the final ordering. That is what makes reranking visible: a CV that was rank 12 under
dense retrieval and rank 1 after reranking proves the technique did something. Without it the
room has to take your word for it.

### Models

| Stage | Model | Network |
| --- | --- | --- |
| Chunk and query embeddings | `intfloat/multilingual-e5-small`, local | none |
| Rerank | `BAAI/bge-reranker-v2-m3`, local | none |
| Query rewrite | `claude-opus-5` | yes, cached |
| Answer generation | `claude-opus-5` | yes, cached |

Both models are multilingual, and they have to be. The corpus is Dutch (arbeidsreglement,
opleidingsplan, kilometervergoeding, SD Worx) and English (CVs, AI policy) in one index, the
questions are Dutch, and a Dutch question must be able to reach an English CV. An
English-only model would fail every question for the wrong reason.

Local embeddings are not only cheaper: they make part 1's honesty point demonstrable. The map
is learned from public training text, so it is poor at itenium's internal jargon, and you can
show that rather than assert it — which is exactly what question 2 does.

### Authentication

`Anthropic()` with no arguments, resolving the OAuth profile written by `ant auth login`
(verified: scope `user:developer user:inference user:profile`, `service_tier: standard`). No
API key, no environment variable, billed to the Claude subscription. The token expires every
8 hours and refreshes on its own; if it is stale on the morning of the talk, `ant auth login`
again. The demo is cache-first, so a stale token cannot break it.

### Caching

Precomputed once, on disk, gitignored:

| Artefact | Built by | Why not live |
| --- | --- | --- |
| `chunks.jsonl` | `build_index.py` | Slow, deterministic |
| `embeddings.npy` | `build_index.py` | Never embed a corpus in front of a room |
| `projection.npy` | `build_index.py` | UMAP takes seconds and is non-deterministic |

Live on every request: BM25 index construction at startup, query embedding, dense and sparse
retrieval, and the RRF merge — all local, all milliseconds over a few thousand vectors. The
toggles flip real retrieval logic; nothing about the demo is faked.

Only the two Claude calls are cached, keyed on `sha256(question + config)` and warmed by
`warm_cache.py` before the talk. A question from the audience is a cache miss: it still works,
it just takes a few seconds. This also answers the outline's warning about failures that
accidentally succeed live — a cached failure stays a failure.

## The UI

FastAPI serving one HTML file. Alpine.js for the wizard and toggles, Plotly from a CDN for
the map, hand-written CSS. No npm, no bundler, no `node_modules`.

**Step 0 — the map.** A scatter of `projection.npy` coloured by source. Hovering a point shows
the chunk text. A search box embeds a query and drops it on the same map with its nearest
neighbours highlighted, so the room watches nearest-neighbour retrieval happen rather than
hearing it described. The outline calls this the demo that makes the session work.

**Steps 1–5 — the ask screen.** Question box with the five questions as preset buttons. The
scoreboard runs down the side and stays visible. Retrieved chunks show their score and their
rank change from the previous stage. The answer shows inline citations from step 5 on.

**Advanced panel.** Collapsed by default, exposes the raw `Config` toggles. It exists for
audience questions and rehearsal, not for the scripted run.

## Failure handling

The app is going to run once, live, in front of colleagues. Every failure mode resolves to
something legible on a projector:

| Failure | Behaviour |
| --- | --- |
| Missing artefacts at startup | One clear error naming the missing file and the command that builds it |
| Missing raw data during build | Error listing what was not found |
| Cache miss, no working credential | The UI says so; it does not crash or hang |
| Claude API error mid-demo | Serve the last cached answer for that question at any config, with a banner |

## Testing

TDD throughout. No test touches the network — `llm.py` is a protocol with a fake
implementation in tests.

- **Chunking:** deterministic ids, correct overlap, heading path preserved.
- **RRF:** known ranked lists produce a known merged order.
- **Cache:** key stability under dict reordering; hit and miss paths.
- **Retrieval, against `sample/`:** the XXimo chunk wins under BM25 and loses under
  dense-only. This is the thesis of the talk expressed as an assertion.
- **Ingestion:** the dropped PII columns appear in no chunk; no ledger chunk states a
  balance; every person in the ledger gets exactly one summary chunk.
- **API:** endpoints return the expected shape.

**The scoreboard test.** `questions.yaml` holds the five questions and their expected verdict
at each of the six steps — 30 assertions — and a test runs the real pipeline against the real
index and fails when reality disagrees. It asserts on *retrieval*, not on generated prose:
deterministic, no LLM call, and it fails for the right reason. It is the defence against a "failing" query quietly
succeeding, and it tells you before the slides are written whether question 4 fails the way
the notes assume.

## Risks

**The questions may not behave.** Against the real corpus, questions 2–4 may fail less
cleanly than the sample assumes, or may not be fixed as cleanly by the matching technique.
The scoreboard test surfaces this early. The fix is rewording the question, which ripples
into the slides — which is the reason slides come after the app.

**Question 3 depends on the real CVs.** Whether five people mention Kubernetes shallowly and
one deeply is a property of the actual 37 CVs, not something the design controls. If the
shape is not there, the technology has to change — the same failure exists for whatever skill
the corpus does have that shape for.

**Question 5 names a person.** "Hoeveel credits heeft X nog?" is asked about a real colleague
whose balance is then read aloud. Worth deciding before the session whether that is fine
(it is internal data in an internal room) or whether to ask it about yourself.

**`uv` is not installed** on the machine this will be built on. The project assumes it; a
venv and pip work as a fallback.
