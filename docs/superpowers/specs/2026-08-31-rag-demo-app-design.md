# RAG demo app — design

The live demo for the [RAG & Embeddings session](../../../notes/Session-Outline.md). One
corpus, five questions, a five-step wizard that mirrors the talk and flips four of them from
red to green. The fifth stays red permanently — that is the point of the session.

## Purpose

The [session outline](../../../notes/Session-Outline.md) is built around a scoreboard: naive
vector RAG answers question 1, fails questions 2–5, and each technique introduced in part 4
fixes exactly one. The app is what the room watches while that happens. It has to make the
difference between "before" and "after" visible on a projector, and it has to be impossible
to break in front of an audience.

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

| Source | Format | Chunking | Role |
| --- | --- | --- | --- |
| Policy PDFs (AI policy, approved AI tools, arbeidsreglement, car change guide, car policy, itenium credits, HR & fleet FAQ) | PDF | ~800 chars, 100 overlap, heading path in metadata | Question 1 — the baseline that works |
| Consultant CVs | PDF/DOCX | Same split, person id + name in metadata | Questions 2–4 — skills, certifications, projects |
| BambooHR export | CSV/JSON | **One record = one chunk**, rendered `Name: … Title: …` | Question 5 — the failure |

The BambooHR chunking is deliberately the wrong thing to do. Records rendered as
near-identical text blobs sit on top of each other in vector space, which is precisely the
demonstration the [demo data note](../../../notes/Demo-Data.md) asks for: retrieval over
chunks is not a substitute for structure.

### Data protection

The corpus is real internal employee data, used internally. Two rules hold anyway:

**Never indexed.** Compensation, performance reviews and goals, and anything touching leave
*reasons*. The five questions do not need them, and leave reasons are health data.

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

`run(question, config) -> Result` returns every candidate with **its rank at each stage**, not
just the final ordering. That is what makes reranking visible: a CV that was rank 12 under
dense retrieval and rank 1 after reranking proves the technique did something. Without it the
room has to take your word for it.

### Models

| Stage | Model | Network |
| --- | --- | --- |
| Chunk and query embeddings | `bge-small-en-v1.5`, local | none |
| Rerank | `bge-reranker-base`, local | none |
| Query rewrite | `claude-opus-5` | yes, cached |
| Answer generation | `claude-opus-5` | yes, cached |

Local embeddings are not only cheaper: they make part 1's honesty point demonstrable. The map
is learned from public training text, so it is poor at itenium's internal jargon, and you can
show that rather than assert it.

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
- **Retrieval, against `sample/`:** the AZ-204 chunk wins under BM25 and loses under
  dense-only. This is the thesis of the talk expressed as an assertion.
- **API:** endpoints return the expected shape.

**The scoreboard test.** `questions.yaml` holds the five questions and their expected verdict
at each of the five steps — 25 assertions — and a test runs the real pipeline against the real
index and fails when reality disagrees. It is the defence against a "failing" query quietly
succeeding, and it tells you before the slides are written whether question 4 fails the way
the notes assume.

## Risks

**The questions may not behave.** Against the real corpus, questions 2–4 may fail less
cleanly than the notes assume, or may not be fixed as cleanly by the matching technique. The
scoreboard test surfaces this early. The fix is rewording the question, which ripples into
the slides — which is the reason slides come after the app.

**`uv` is not installed** on the machine this will be built on. The project assumes it; a
venv and pip work as a fallback.
