# Session outline — RAG & Embeddings

## The spine

Do not present this as a tour of techniques. Present it as **one dataset and five questions**,
of which the naive pipeline answers exactly one. Then fix them one at a time. Every section
earns its place by killing a specific failing question, and the graph half arrives as the
answer to the two questions that retrieval tuning *cannot* fix.

The dataset is consultant data from BambooHR plus CVs and project sheets — see
[Demo Data](Demo-Data.md), including what not to export.

Put the five questions on screen in part 2 and leave them up as a scoreboard all session.

| # | Question | Naive RAG does | Fixed in |
| --- | --- | --- | --- |
| 1 | "What is our policy on training budget?" | ✅ **answers it correctly** | — the baseline |
| 2 | "Who has the **AZ-204** certification?" | returns the AZ-104 and AZ-400 people | Part 4 — hybrid + BM25 + RRF |
| 3 | "Who is our **strongest** Kubernetes consultant?" | five people who mention it once in passing | Part 4 — reranking |
| 4 | "**How many** consultants are available from October?" | invents a confident number | Part 6 — graph + text2cypher |
| 5 | "Which skills are we **collectively** short on?" | generic waffle about upskilling | Part 7 — GraphRAG global search |

Question 1 works from the start — that matters, because a session where nothing works is a
session nobody believes. It is a policy document: prose, semantically distinctive, and the
answer lives in one chunk. This is genuinely what vector RAG is good at.

Question 2 is the cheap fix that makes people feel clever. Question 3 is the one they will
recognise from their own systems. **Question 4 is the pivot** — where the room sees that no
amount of retrieval tuning helps. Question 5 sells GraphRAG.

Everyone in the room is *in* this dataset, which is worth a great deal. Nobody has to be
persuaded that the questions matter.

---

## 2-hour version

### Part 0 — Why we are here (10 min) · theory
LLM limitations, finetuning vs RAG, retrieval + augmented generation.
Source: [Essential GraphRAG](Essential-GraphRAG.md), [LLM Training](LLM-Training.md).

Keep it short. Most of the room already believes RAG is worth doing — do not spend twenty
minutes selling something nobody is arguing against.

### Part 1 — Embeddings (20 min) · theory + demo
Source: [Embedding Models](Embedding-Models.md), [Vector Similarity Search](Vector-Similarity-Search.md).

> **Demo** — embed a dozen sentences from the CVs, print the cosine similarity matrix. Show
> two sentences with no shared words scoring high. Then show `AZ-204` and `AZ-104` scoring
> ~0.99 despite being different certifications. That one result sets up question 2 and the
> entire hybrid search section two parts later.

Cover: encoder → pooling → vector, and that the geometry reflects *what the model was trained
to consider similar*; the model lineup and MTEB; dimensions and cost; normalization
(dot product ≡ cosine); the query/passage prefix gotcha; token limits.

### Part 2 — Naive RAG, end to end (20 min) · demo-led
Build the whole pipeline in front of them: chunk → embed → store → retrieve → generate.
Keep it under ~50 lines and resist adding anything clever.

Then run the five questions. **One works. Four fail.** Put the scoreboard up.

Worth naming explicitly here: the BambooHR records chunk into near-identical blobs
("Name: … Title: … Department: …") that sit on top of each other in vector space. That is
not a bug in your pipeline, it is structured data being forced through a text-retrieval
pipe — and it is the thesis of the whole session.

### Part 3 — Where the vectors live (10 min) · theory
Source: [Vector Indexes](Vector-Indexes.md), [Vector Stores](Vector-Stores.md).

Flat vs HNSW and the `ef_search` recall dial, quantization as the cost lever, and the
pre-filter vs post-filter trap. Then the storage menu with an opinion: **if Postgres is
already in your stack, start with pgvector.**

> **Ninety-second demo** — same query, same data, add a selective metadata filter, watch the
> results go empty. It is the kind of bug people recognise from their own logs.

### Part 4 — Fixing retrieval (30 min) · demo-led
The heart of the session and the part people will actually use.
Source: [Hybrid Search](Hybrid-Search.md), [Reranking](Reranking.md),
[Step-back prompting](Step-back-Prompting.md).

- **Hybrid search** — BM25 alongside vectors, merged with RRF (`1/(k+rank)`, k≈60). Show the
  ten-line RRF function; people expect something harder. Question 2 passes. ✅
- **Reranking** — retrieve 50, cross-encode, keep 5. The Kubernetes expert was at rank 12
  under a pile of passing mentions. Question 3 passes. ✅
- **Query rewriting** — take question 3's harder phrasing ("who can take over the Kubernetes
  work at ACME in October") and show [step-back prompting](Step-back-Prompting.md) broadening
  it. Mention HyDE and multi-query as siblings.
- **Context assembly** — "lost in the middle": fewer, better-ordered chunks beat more chunks.

Three of five now pass. Questions 4 and 5 are still broken **and no amount of retrieval
tuning will fix them.** Say that out loud — it is the pivot of the whole session.

### Part 5 — Break (10 min)

### Part 6 — Structure: knowledge graphs (25 min) · theory + demo
Source: [Essential GraphRAG](Essential-GraphRAG.md).

Counting, filtering, sorting and aggregating are simply not what chunk retrieval does.
Question 4 does not fail by returning nothing — it fails by returning a **confident wrong
number**, which is worse and much scarier to watch.

Build the graph: consultants, skills, certifications, projects, clients, availability. Most
of it comes from BambooHR fields directly; the manager field gives you a real org hierarchy
for free. Extract the rest from CVs with a JSON schema.

**Entity resolution** earns its slide here: `Wouter Van Schandevijl` in BambooHR,
`W. Van Schandevijl` on the project sheet, `wouter.van.schandevijl@itenium.be` in the
timesheet export. Three nodes, one person, and your count is wrong until they merge.

Then text2cypher — two minutes of Cypher syntax first, then the prompt template from the
book notes. Question 4 passes. ✅

> Cypher is not Neo4j-only: openCypher runs on Memgraph, Neptune and Apache AGE, and ISO GQL
> (2024) derives from it. See gap 12 in [Gaps](Gaps.md).

### Part 7 — GraphRAG (20 min) · theory + demo
Entity extraction, then community detection and summaries. Global search — map over community
summaries, reduce to an answer — handles question 5, because "which skills are we collectively
short on" is not in any single chunk. ✅

Be honest about cost: an LLM call per chunk plus one per community summary. Then local search
as the cheaper everyday path, and LazyGraphRAG / DRIFT as where Microsoft took it next.

### Part 8 — Did any of this work? (15 min) · theory
Source: gap 10 in [Gaps](Gaps.md).

Retrieval metrics first (recall@k, MRR, nDCG@k) — if retrieval is broken, generation metrics
only tell you *that* something is wrong. Then RAGAS for answer quality. Then the honest part:
building the golden dataset is the actual work, and there is no shortcut.

Your five questions are the beginning of that golden set. Say so — it closes the loop.

### Part 9 — Production and when not to (10 min) · theory
Source: gaps 6–9 and 11 in [Gaps](Gaps.md), and [Demo Data](Demo-Data.md).

Ingestion beyond chunking, citations, caching and cost. **Access control gets top billing
here** — with this dataset it is not hypothetical: should a consultant be able to retrieve a
chunk about a colleague? Consider demoing per-user filtering rather than only describing it.
It is the most production-relevant thing in the session and almost nobody covers it.

Close on **when not to reach for this**: long context sometimes just wins, keyword search is
sometimes enough, and GraphRAG's indexing bill is not always repaid. Ending on the limits is
more credible than a victory lap.

---

## 60-minute cut

Keep the spine, drop the depth.

| Keep | Minutes |
| --- | --- |
| Part 1 — embeddings, with the AZ-204 similarity demo | 10 |
| Part 2 — naive pipeline + the five questions | 15 |
| Part 4 — hybrid + RRF, and reranking only | 15 |
| Part 6 — graph + text2cypher, question 4 | 12 |
| Part 9 — access control, cost, when not to | 8 |

Cut parts 0, 3, 7 and 8 entirely. Say up front that evaluation and GraphRAG proper are the
follow-up session — do not compress them, they will just land badly.

---

## Practical notes

- **Read [Demo Data](Demo-Data.md) before exporting anything.** Compensation, performance
  reviews and leave reasons should never reach the vector store, and a pseudonymized snapshot
  costs you nothing in the demo.
- **Pre-compute every embedding and every graph build.** Do not run entity extraction live —
  it is slow, costs money, and is non-deterministic in front of an audience. Commit the
  artefacts and load them.
- **Keep the name messiness.** If you pseudonymize, preserve the three-spellings-per-person
  problem. Question 4's entity resolution moment depends on it.
- **Have the failing output saved.** If a "failing" query accidentally succeeds live, the
  narrative collapses. Screenshot the failures beforehand.
- **The five questions are the handout.** Anyone who leaves remembering only "vectors cannot
  count" has got their money's worth.
- Sources for every section are in [Gaps](Gaps.md). The P1 gaps are now written; P2 and P3
  are still outlines.
