# Session outline — RAG & Embeddings

**Audience:** no prior exposure to RAG, embeddings or vector search. Assume the words are
new, not just the techniques. See [Foundations](Foundations.md).
**Format:** ~2 hours, you drive every demo, the room watches.
**Scope:** vector RAG only. GraphRAG is deliberately out — it is not in the title, and a room
meeting embeddings for the first time cannot absorb community detection in the same sitting.

## The spine

One dataset, five questions, of which the naive pipeline answers exactly one. Each fix kills
a specific question. The **fifth is never fixed** — it is the cliffhanger that earns a second
session.

Dataset: consultant data from BambooHR plus CVs and project sheets — see
[Demo Data](Demo-Data.md), including what must not be exported.

Put the questions on screen in part 3 and leave them up as a scoreboard.

| # | Question | Naive RAG does | Fixed in |
| --- | --- | --- | --- |
| 1 | "What is our policy on training budget?" | ✅ **answers it correctly** | — the baseline |
| 2 | "Who has the **AZ-204** certification?" | returns the AZ-104 and AZ-400 people | Part 4 — hybrid search |
| 3 | "Who is our **strongest** Kubernetes consultant?" | five people who mention it once | Part 4 — reranking |
| 4 | "Who can take over the ACME work **in October**?" | finds nothing useful | Part 4 — query rewriting |
| 5 | "**How many** consultants are free from October?" | invents a confident number | ❌ **never** — next session |

Question 1 working matters: a session where nothing works is a session nobody believes, and
it shows what vector RAG is genuinely good at. Question 5 failing *permanently* is the point
of the ending — see part 6.

Everyone in the room is in this dataset. Nobody needs persuading that the questions matter.

---

## Part 0 — The problem (15 min)

**No architecture yet.** Open by asking a model a question about itenium and letting the room
watch it invent a fluent, confident, wrong answer. That is the motivation, and it is more
persuasive than any slide.

Then: the model learned from text up to a cutoff, knows nothing private, and answers anyway.
Two fixes — retrain it (expensive, slow, still unreliable for facts) or **show it the
documents at question time**. The second is RAG.

Land the **open-book exam** analogy and use nothing else all session. Pre-empt the three
things people are already thinking: this is not training, it does not remember, and it can
still be wrong.

Source: [Foundations](Foundations.md) §1–2.

## Part 1 — Embeddings (25 min)

The longest theory block, because the session is named after it and it is the one idea
everything else rests on.

Keyword search first — everyone knows it — and where it breaks: "who knows container
orchestration" misses a CV that says "5 years Kubernetes". So we need to match meaning.

**Show a real vector before defining one.** Then: an embedding model gives text *coordinates
on a map of meaning*, and near means similar.

> **The demo that makes the session work.** Embed thirty sentences from the CVs, squash to
> 2D, plot. Infrastructure people cluster here, frontend there, data over there — and nobody
> wrote those groupings. Let the room look at it in silence. A beginner who *sees* the
> clustering understands embeddings; one who only hears "high-dimensional vector space" does
> not.

Then vector search: embed the question too, return the nearest chunks.

Two honesty points, both cheap: the map is **learned** from training examples, not
discovered, so it is poor at your internal jargon; and there are **two different models** in
play — one makes coordinates, one writes answers. Draw them as separate boxes and keep them
separate all session.

Source: [Foundations](Foundations.md) §3–4, [Embedding Models](Embedding-Models.md) for depth
you will mostly not use.

## Part 2 — Chunking and the pipeline (15 min)

Why documents get chopped: you cannot put a 40-page document at one point on the map. **Index
cards.** Size, overlap, and where to cut.

Then build the whole thing live, under ~50 lines, and draw the six-box diagram
([Foundations](Foundations.md) §6). Refer back to it every time something changes later —
"this modifies *this* box" is what keeps a beginner room oriented.

## Part 3 — Run the questions (10 min)

One works. Four fail. Scoreboard up, and leave it up.

Worth naming: the BambooHR records chunk into near-identical blobs (`Name: … Title: …`) that
sit on top of each other on the map. That is structured data being forced through a
text-retrieval pipe, and it is why question 5 is doomed — foreshadow it here, do not explain
it yet.

## Break (10 min)

## Part 4 — Making it work (30 min)

The heart of the session. Three fixes, each demoed against its failing question. Keep every
explanation at the level of *what it does*, not *how it is built*.

- **Hybrid search** (question 2 ✅) — run old-fashioned keyword search alongside the meaning
  search and merge the results, because they fail at different things. Vectors are hopeless
  at `AZ-204` versus `AZ-104`; keyword search is perfect at it. Show the ten-line merge
  function — people expect something harder.
  → [Hybrid Search](Hybrid-Search.md)
- **Reranking** (question 3 ✅) — retrieval is fast and rough, so fetch 50 candidates and let
  a slower, more careful model re-sort them and keep the best 5. The real Kubernetes expert
  was sitting at rank 12 under CVs that mention it once.
  → [Reranking](Reranking.md)
- **Query rewriting** (question 4 ✅) — the question as typed is often a bad search query.
  Have the model rewrite it first: broaden the over-specific ones
  ([step-back prompting](Step-back-Prompting.md)), split the compound ones.

Four of five now pass.

## Part 5 — "How do I know it isn't making this up?" (10 min)

Someone will have been waiting to ask this since part 0. Answer it properly: keep track of
which chunk every claim came from, show the citation, link back to the source document.

Two things worth saying plainly — a citation is not proof (models cite plausibly and
wrongly, so it needs checking), and a system that says **"I don't know"** on unanswerable
questions is more useful than one that never does. Demo the refusal on a question the corpus
genuinely cannot answer.

Source: [Citations](Citations.md).

## Part 6 — Where this stops (10 min)

Point at question 5, still red.

*How many consultants are free from October* is not a retrieval problem. There is no chunk
that contains the answer — it has to be **counted** across records. You can improve chunking,
embeddings, reranking and rewriting forever and it will never work, because retrieval finds
passages that resemble the question and this question needs arithmetic.

> **The line to leave them with: vectors cannot count.**

Then name the answer without teaching it: pull the facts out into a network of things and
relationships, and query that instead. That is GraphRAG, that is the book this came from, and
that is the next session.

Close with the honest limits from [When Not To RAG](When-Not-To-RAG.md) — sometimes plain
keyword search is enough, and sometimes the whole corpus just fits in the prompt and none of
this is needed. Ending on the limits is more credible than a victory lap.

---

## 60-minute cut

| Keep | Minutes |
| --- | --- |
| Part 0 — the invented answer, open-book exam | 10 |
| Part 1 — embeddings and the 2D cluster plot | 15 |
| Parts 2–3 — pipeline and the five questions | 15 |
| Part 4 — hybrid search and reranking only | 15 |
| Part 6 — vectors cannot count | 5 |

Drop query rewriting and citations. Do **not** drop the cluster plot or the scoreboard —
they are what the room remembers.

---

## Parked for later sessions

None of this is lost; it is written up and waiting.

**Session 2 — GraphRAG**, which the five-question cliffhanger sets up:
[Essential GraphRAG](Essential-GraphRAG.md), [Cypher Primer](Cypher-Primer.md),
[GraphRAG Since The Book](GraphRAG-Since-The-Book.md).

**Session 3 — putting RAG in production**, for the people who want to build one:
[Vector Indexes](Vector-Indexes.md), [Vector Stores](Vector-Stores.md),
[Ingestion](Ingestion.md), [Access Control](Access-Control.md),
[Cost and Caching](Cost-And-Caching.md), [Evaluation](Evaluation.md).

Access control deserves a flag: with this dataset it is not theoretical, and it is the
question that decides whether such a tool is allowed to exist at itenium at all.

---

## Practical notes

- **Read [Demo Data](Demo-Data.md) before exporting anything.** Compensation, performance
  reviews and leave reasons must not reach the vector store; a pseudonymized snapshot costs
  nothing in the demo.
- **Hand out the [Glossary](Glossary.md) on paper at the start.** A beginner room loses more
  people to undefined vocabulary than to hard ideas.
- **Pre-compute every embedding.** Do not embed live — it is slow and it fails in front of an
  audience. Commit the artefacts and load them.
- **Have the failing output saved.** If a "failing" query accidentally succeeds live, the
  narrative collapses. Screenshot the failures beforehand.
- **One analogy, used consistently.** Open-book exam for RAG, map for embeddings, index cards
  for chunks. Four clever metaphors are worse than one repeated.
- **Offer the repo afterwards.** You drive during the session; hand out something runnable so
  the hands-on people have somewhere to go.
- **The five questions are the handout.** Anyone who leaves remembering only "vectors cannot
  count" has got their money's worth.
