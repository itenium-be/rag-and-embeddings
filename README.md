RAG and Embeddings
==================

Notes for the itenium session on **Essential GraphRAG** by [[Tomaž Bratanič]] and [[Oskar Hane]]
([[Manning]]): build accurate, explainable, context-aware GenAI applications.

# Notes

| Note | Covers |
| --- | --- |
| [Essential GraphRAG](notes/Essential-GraphRAG.md) | Book notes: LLM limitations, RAG, hybrid & advanced retrieval, text2cypher, agentic RAG, knowledge graph construction, MS GraphRAG, evaluation |
| [Vector Similarity Search](notes/Vector-Similarity-Search.md) | Vector index, similarity functions, embedding models, text chunking |
| [LLM Training](notes/LLM-Training.md) | Pretraining, supervised finetuning, reward modeling, reinforcement learning |
| [Step-back prompting](notes/Step-back-Prompting.md) | Broadening a question before retrieval, with the system prompt |

# Preparing the session

| Note | Covers |
| --- | --- |
| [Session outline](notes/Session-Outline.md) | 2-hour running order (and a 60-minute cut), built around five questions of which the naive pipeline answers one |
| [Demo data](notes/Demo-Data.md) | Consultant data from BambooHR plus CVs — what to pull, and what must not reach the vector store |
| [Gaps](notes/Gaps.md) | What the book notes do not cover but the session needs, prioritised, plus corrections to the existing notes |

# Session material (P1 gaps, written)

| Note | Covers |
| --- | --- |
| [Embedding models](notes/Embedding-Models.md) | What the vector is, the model lineup, MTEB, dimensions and cost, Matryoshka, the query/passage prefix gotcha |
| [Hybrid search](notes/Hybrid-Search.md) | Where dense retrieval fails, BM25, and Reciprocal Rank Fusion |
| [Reranking](notes/Reranking.md) | Bi-encoder vs cross-encoder, what to run, and "lost in the middle" |
| [Vector indexes](notes/Vector-Indexes.md) | Brute force, HNSW and its dials, quantization, and the metadata filter trap |
| [Vector stores](notes/Vector-Stores.md) | pgvector vs the dedicated stores, and how to choose |

# Production concerns (P2)

| Note | Covers |
| --- | --- |
| [Ingestion](notes/Ingestion.md) | Parsing before chunking, deterministic chunk IDs, deletes, and re-embedding as a migration |
| [Access control](notes/Access-Control.md) | The index is a copy with different permissions — filtering, Postgres RLS, drift, and four ways it leaks |
| [Citations](notes/Citations.md) | Carrying provenance end to end, verifying the citation, and designing the refusal |
| [Cost and caching](notes/Cost-And-Caching.md) | Where the money goes, what GraphRAG indexing costs, prompt caching, semantic caching risks |

# Framing and depth (P3)

| Note | Covers |
| --- | --- |
| [Evaluating retrieval](notes/Evaluation.md) | recall@k, MRR, nDCG, the recall@50-vs-@5 diagnostic, and building the golden set |
| [When not to reach for this](notes/When-Not-To-RAG.md) | Long context, plain keyword search, text2sql, and the GraphRAG cost test |
| [Cypher primer](notes/Cypher-Primer.md) | Enough Cypher to read what text2cypher generates — and why it is not Neo4j-only |
| [GraphRAG since the book](notes/GraphRAG-Since-The-Book.md) | LazyGraphRAG, DRIFT search, and Leiden vs Louvain |

# Reading order

Start with [Essential GraphRAG](notes/Essential-GraphRAG.md) — the other three are the
supporting notes it links out to, in the order they are first referenced.

Wikilinks that are still `[[bracketed]]` point at notes that live in the wider Obsidian
vault and were not part of this export.
