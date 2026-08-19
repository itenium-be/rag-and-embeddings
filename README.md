RAG and Embeddings
==================

Notes for the itenium session on **RAG & Embeddings**, drawn from **Essential GraphRAG** by
[[Tomaž Bratanič]] and [[Oskar Hane]] ([[Manning]]): build accurate, explainable,
context-aware GenAI applications.

**Session one assumes no prior exposure** — no RAG, no embeddings, no vector search. It
covers vector RAG only and ends on the one question vectors can never answer. GraphRAG is
session two; production concerns are session three.

# Notes

| Note | Covers |
| --- | --- |
| [Essential GraphRAG](notes/Essential-GraphRAG.md) | Book notes: LLM limitations, RAG, hybrid & advanced retrieval, text2cypher, agentic RAG, knowledge graph construction, MS GraphRAG, evaluation |
| [Vector Similarity Search](notes/Vector-Similarity-Search.md) | Vector index, similarity functions, embedding models, text chunking |
| [LLM Training](notes/LLM-Training.md) | Pretraining, supervised finetuning, reward modeling, reinforcement learning |
| [Step-back prompting](notes/Step-back-Prompting.md) | Broadening a question before retrieval, with the system prompt |

# Start here

| Note | Covers |
| --- | --- |
| [Session outline](notes/Session-Outline.md) | 2-hour running order (and a 60-minute cut), built around five questions of which the naive pipeline answers one |
| [Foundations](notes/Foundations.md) | The beginner material — what the model doesn't know, the open-book exam, embeddings as a map of meaning, and what to leave out |
| [Glossary](notes/Glossary.md) | Plain-language definitions, meant to be handed out on paper at the start |
| [Demo data](notes/Demo-Data.md) | Consultant data from BambooHR plus CVs — what to pull, and what must not reach the vector store |
| [Gaps](notes/Gaps.md) | What the book notes do not cover but the sessions need, prioritised, plus corrections to the existing notes |

# Session one — RAG & Embeddings

| Note | Covers |
| --- | --- |
| [Embedding models](notes/Embedding-Models.md) | What the vector is, the model lineup, MTEB, dimensions and cost, the query/passage prefix gotcha |
| [Hybrid search](notes/Hybrid-Search.md) | Where dense retrieval fails, BM25, and Reciprocal Rank Fusion — fixes question 2 |
| [Reranking](notes/Reranking.md) | Retrieve wide, re-sort carefully, keep few — fixes question 3 |
| [Step-back prompting](notes/Step-back-Prompting.md) | Broadening an over-specific question — fixes question 4 |
| [Citations](notes/Citations.md) | "How do I know it isn't making this up?" — provenance, verification, and the refusal |
| [When not to reach for this](notes/When-Not-To-RAG.md) | The closing note: long context, plain keyword search, and where RAG stops paying |

# Session two — GraphRAG

Set up by question 5, which session one leaves permanently unfixed.

| Note | Covers |
| --- | --- |
| [Essential GraphRAG](notes/Essential-GraphRAG.md) | The book notes: knowledge graph construction, text2cypher, agentic RAG, MS GraphRAG, evaluation |
| [Cypher primer](notes/Cypher-Primer.md) | Enough Cypher to read what text2cypher generates — and why it is not Neo4j-only |
| [GraphRAG since the book](notes/GraphRAG-Since-The-Book.md) | LazyGraphRAG, DRIFT search, and Leiden vs Louvain |

# Session three — putting RAG in production

| Note | Covers |
| --- | --- |
| [Vector indexes](notes/Vector-Indexes.md) | Brute force, HNSW and its dials, quantization, and the metadata filter trap |
| [Vector stores](notes/Vector-Stores.md) | pgvector vs the dedicated stores, and how to choose |
| [Ingestion](notes/Ingestion.md) | Parsing before chunking, deterministic chunk IDs, deletes, re-embedding as a migration |
| [Access control](notes/Access-Control.md) | The index is a copy with different permissions — filtering, Postgres RLS, drift, four leak paths |
| [Cost and caching](notes/Cost-And-Caching.md) | Where the money goes, what GraphRAG indexing costs, prompt caching, semantic caching risks |
| [Evaluating retrieval](notes/Evaluation.md) | recall@k, MRR, nDCG, the recall@50-vs-@5 diagnostic, and building the golden set |

# Supporting notes

| Note | Covers |
| --- | --- |
| [Vector similarity search](notes/Vector-Similarity-Search.md) | Original book notes: vector index, similarity functions, embedding models, chunking |
| [LLM training](notes/LLM-Training.md) | Pretraining, supervised finetuning, reward modeling, reinforcement learning |

# Reading order

To prepare session one: [Session outline](notes/Session-Outline.md) →
[Foundations](notes/Foundations.md) → [Demo data](notes/Demo-Data.md) → the session one
notes in table order.

For the source material the whole thing came from, read
[Essential GraphRAG](notes/Essential-GraphRAG.md).

Wikilinks that are still `[[bracketed]]` point at notes that live in the wider Obsidian
vault and were not part of this export.
