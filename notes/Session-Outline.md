# Session outline — RAG & Embeddings

## The spine

Do not present this as a tour of techniques. Present it as **one dataset and five questions
that the naive pipeline gets wrong**, then fix them one at a time. Every section earns its
place by killing a specific failing question, and the graph half arrives as the answer to
the two questions that retrieval tuning *cannot* fix.

Put the five questions on screen in part 2 and leave them up as a scoreboard all session.

| # | Question | Naive RAG fails because | Fixed in |
| --- | --- | --- | --- |
| 1 | "What are the payment terms in contract **INV-2024-0871**?" | exact identifiers are invisible to dense vectors | Part 4 — hybrid + BM25 |
| 2 | "What did we agree with **itenium BVBA**?" | same entity, three spellings | Part 6 — entity resolution |
| 3 | "Which team did X play for in 2007–2008?" | over-specific query, no chunk matches | Part 5 — step-back / query rewriting |
| 4 | "**How many** active contracts do we have?" | counting over unstructured chunks | Part 6 — graph + text2cypher |
| 5 | "What are the **main themes** across all contracts?" | no single chunk contains the answer | Part 7 — GraphRAG global search |

Questions 1 and 3 are cheap fixes that make people feel clever. Question 4 is where the room
realises vectors have a ceiling. Question 5 is the one that sells GraphRAG.

---

## 2-hour version

### Part 0 — Why we are here (10 min) · theory
LLM limitations, finetuning vs RAG, retrieval + augmented generation.
Source: [Essential GraphRAG](Essential-GraphRAG.md), [LLM Training](LLM-Training.md).

Keep it short. Most of the room already believes RAG is worth doing — do not spend twenty
minutes selling something nobody is arguing against.

### Part 1 — Embeddings (20 min) · theory + demo
What the vector actually is, how models differ, what it costs.
Source: [Vector Similarity Search](Vector-Similarity-Search.md) + gap 1 in [Gaps](Gaps.md).

> **Demo** — embed a dozen sentences, print the cosine similarity matrix. Show two sentences
> with no shared words scoring high, and `INV-2024-0871` vs `INV-2024-0872` scoring ~0.99
> despite being different contracts. That single result sets up question 1 and the entire
> hybrid search section two parts later.

Cover: encoder → pooling → vector; model lineup and MTEB; dimensions and cost; normalization
(dot product ≡ cosine on normalized vectors); token limits.

### Part 2 — Naive RAG, end to end (20 min) · demo-led
Build the whole pipeline in front of them: chunk → embed → store → retrieve → generate.
Keep it under ~50 lines and resist adding anything clever.

Then run the five questions. Two work. Three fail. Put the scoreboard up.

Cover while building: chunk size, overlap, contextual embedding, the vector index as an
*approximate* nearest-neighbour structure.

### Part 3 — Where the vectors live (10 min) · theory
The shortest section, but the one people ask about afterwards.
Source: gaps 3 and 4 in [Gaps](Gaps.md).

Flat vs HNSW (and the `ef_search` recall/latency dial), quantization as the cost lever, and
the pre-filter vs post-filter trap. Then the storage menu, with an opinion: **if Postgres is
already in your stack, start with pgvector and only leave when you can name the reason.**

### Part 4 — Fixing retrieval (30 min) · demo-led
The heart of the session, and the part people will actually use.
Source: gaps 2 and 5 in [Gaps](Gaps.md).

- **Hybrid search** — BM25 alongside vectors, merged with Reciprocal Rank Fusion
  (`1/(k+rank)`, k≈60). Re-run question 1: it now passes. ✅
- **Reranking** — retrieve 50, cross-encode, keep 5. Show the ordering change on a query
  where the right chunk was ranked 11th.
- **Query rewriting** — [step-back prompting](Step-back-Prompting.md) fixes question 3 ✅;
  mention HyDE and multi-query as siblings.
- **Chunking revisited** — parent document retriever, contextual embedding.

Three of five questions now pass. Questions 2 and 4 are still broken *and no amount of
retrieval tuning will fix them.* Say that out loud — it is the pivot of the whole session.

### Part 5 — Break (10 min)

### Part 6 — Structure: knowledge graphs (25 min) · theory + demo
Source: [Essential GraphRAG](Essential-GraphRAG.md).

Why counting, filtering, sorting and aggregating are simply not what chunk retrieval does.
Extracting structured data with a JSON schema; keeping the source chunks alongside the graph.
**Entity resolution** — itenium / itenium BV / itenium BVBA — fixes question 2. ✅

Then text2cypher. Two minutes of Cypher syntax first, then the prompt template from the
book notes. Question 4 passes. ✅

> Mention that Cypher is not Neo4j-only — openCypher runs on Memgraph, Neptune and Apache
> AGE, and ISO GQL (2024) is derived from it. See gap 12 in [Gaps](Gaps.md).

### Part 7 — GraphRAG (20 min) · theory + demo
Microsoft's two-stage process: entity extraction, then community detection and summaries.
Global search (map/reduce over community summaries) answers question 5. ✅

Be honest about the cost here — an LLM call per chunk plus one per community summary. Then
local search as the cheaper everyday path, and LazyGraphRAG / DRIFT as where it went next.

### Part 8 — Did any of this work? (15 min) · theory
Source: gap 10 in [Gaps](Gaps.md).

Retrieval metrics first (recall@k, MRR, nDCG@k) — because if retrieval is broken, generation
metrics only tell you *that* something is wrong. Then RAGAS for answer quality: context
recall, faithfulness, answer correctness. Then the honest part: building the golden dataset
is the actual work, and there is no shortcut.

### Part 9 — Production and when not to (10 min) · theory
Source: gaps 6–9 and 11 in [Gaps](Gaps.md).

Ingestion beyond chunking (tables and OCR are where projects stall), access control and
multi-tenancy, citations, caching and cost. Close on **when not to reach for this**: long
context sometimes just wins, keyword search is sometimes enough, and GraphRAG's indexing
bill is not always repaid.

Ending on the limits is more credible than ending on a victory lap.

---

## 60-minute cut

Keep the spine, drop the depth.

| Keep | Minutes |
| --- | --- |
| Part 1 — embeddings, with the similarity-matrix demo | 10 |
| Part 2 — naive pipeline + the five questions | 15 |
| Part 4 — hybrid + RRF, and reranking only | 15 |
| Part 6 — graph + text2cypher, question 4 | 12 |
| Part 9 — cost and when not to | 8 |

Cut parts 0, 3, 7 and 8 entirely. Say up front that evaluation and GraphRAG proper are the
follow-up session — do not try to compress them, they will just land badly.

---

## Practical notes

- **One dataset all session.** Contracts work well: they are boring enough that nobody
  argues about the domain, and they naturally have identifiers, duplicate entities, and
  aggregate questions. A public corpus (EDGAR filings, EU legislation) avoids showing
  anything internal.
- **Pre-compute every embedding and every graph build.** Do not run entity extraction live —
  it is slow, costs money, and is non-deterministic in front of an audience. Commit the
  artefacts and load them.
- **Have the failing output saved.** If a "failing" query accidentally succeeds live, the
  narrative collapses. Screenshot the failures beforehand.
- **The five questions are the handout.** Anyone who leaves remembering only "vectors cannot
  count" has got their money's worth.
- Sources for every section are in [Gaps](Gaps.md); the gaps marked P1 need writing before
  this outline is deliverable.
