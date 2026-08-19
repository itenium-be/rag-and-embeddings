# Content gaps for a "RAG & Embeddings" session

## Why there are gaps

Everything in this repo comes from [Essential GraphRAG](Essential-GraphRAG.md). The book
treats vector RAG as *background* so it can spend its pages on the graph. That is the right
call for a book called Essential GraphRAG, and the wrong balance for a session called
**RAG & Embeddings**.

| Note | Words |
| --- | --- |
| [Essential GraphRAG](Essential-GraphRAG.md) | 1726 |
| [Vector Similarity Search](Vector-Similarity-Search.md) | 242 |
| [Step-back prompting](Step-back-Prompting.md) | 149 |
| [LLM Training](LLM-Training.md) | 69 |

The embeddings half of the session title is the thinnest note in the repo.

None of these terms appear anywhere in the notes:

> BM25 · HNSW · IVF · DiskANN · pgvector · Qdrant · Weaviate · Milvus · Pinecone · Chroma ·
> Neo4j · LangChain · LlamaIndex · MTEB · cross-encoder · ColBERT · HyDE · reciprocal rank
> fusion · quantization · recall@k · MRR · caching · OCR · citations · access control ·
> multi-tenancy · long context

`nDCG` appears exactly once, inside a quoted RavenDB blog snippet in
[Vector Similarity Search](Vector-Similarity-Search.md).

---

## P1 — fill these first

These four are what an audience expects from the session title and what they will actually
use on Monday.

### 1. Embeddings, properly

**Missing:** what the vector *is* (a trained encoder plus a pooling step, learned with
contrastive objectives); named models and how to pick one; token limits; normalization;
dimension/cost tradeoffs.

**Why it matters:** the session is half-named after this and the current note covers it in
a paragraph. "Which embedding model should I use, and what does it cost" is the first
question anyone asks.

**Suggested note:** `Embedding-Models.md`
- Encoder → pooling (CLS vs mean) → vector; contrastive training is why similar texts land close
- The lineup: OpenAI `text-embedding-3-small` / `-large`, Cohere Embed, Voyage,
  open-weights BGE / E5 / GTE — and MTEB as the leaderboard to check, with the caveat that
  leaderboard rank rarely survives contact with your own corpus
- Dimensions: 384 → 3072, and what that costs in storage and query time
- Matryoshka (MRL) truncation: `text-embedding-3` vectors can be cut down without re-embedding
- Input token limits (~8k for the OpenAI models) and what happens when you exceed them
- Normalization: on L2-normalized vectors, dot product *is* cosine — which is why most
  stores normalize on write
- Domain-specific and multilingual models; code embeddings; a word on multimodal (CLIP)

### 2. Hybrid search and how results actually get merged

**Missing:** BM25 by name, and **Reciprocal Rank Fusion**.

**Why it matters:** this is the highest value-per-minute topic in the whole session. Pure
vector search fails on exact identifiers, product codes, names and acronyms — precisely the
queries that make a demo look broken. The current notes say hybrid search "combines exact
keyword matches from a full text search index with the vector search" and stop there,
never explaining *how* two ranked lists become one.

**Suggested note:** `Hybrid-Search.md`
- Lexical retrieval: TF-IDF → BM25, and what BM25's term saturation actually buys you
- Where dense retrieval wins and where lexical wins — with example queries for each
- RRF: score each document as the sum of `1 / (k + rank)` across the lists it appears in
  (k ≈ 60 by convention). No score normalization needed, which is the whole appeal
- Score-based alternatives and why they are fiddlier (incomparable score scales)
- Learned sparse retrieval (SPLADE) as the middle ground

### 3. The vector index is currently a black box

**Missing:** any named index structure, any recall/latency knob, quantization, and the
filtering trap.

**Why it matters:** [Vector Similarity Search](Vector-Similarity-Search.md) describes the
index as "a data structure that makes it easy to find similar vectors" and correctly notes
it returns *approximate* neighbours — but never says what the approximation costs or how to
tune it. Meanwhile the book notes recommend metadata prefiltering without mentioning that
filters and ANN interact badly.

**Suggested note:** `Vector-Indexes.md`
- Brute force / flat: exact, fine up to surprisingly large collections — start here
- HNSW: the graph, and the three knobs (`M`, `ef_construction`, `ef_search`) that trade
  recall against latency and memory
- IVF and DiskANN in one line each, for when the corpus outgrows RAM
- Quantization: scalar, binary (~32× smaller), product quantization — this is where the
  hosting bill goes down, with a recall cost you should measure
- **Filtering**: pre-filter vs post-filter. Post-filtering can return far fewer than `k`
  results; naive pre-filtering can wreck HNSW's graph traversal. This is a real production
  trap and the notes currently recommend the technique without the warning

### 4. Storage: where do the vectors actually live

**Missing:** every product name.

**Why it matters:** for an itenium audience "do I just use pgvector" is probably the single
most relevant decision in the session.

**Suggested note:** `Vector-Stores.md`
- pgvector / pgvectorscale — the default answer when Postgres is already in the stack
- Dedicated: Qdrant, Weaviate, Milvus, Chroma, Pinecone
- Search engines that grew vectors: Elasticsearch, OpenSearch, Redis
- Neo4j's vector index — the bridge to the GraphRAG half of the notes
- Choosing on: filtering support, hybrid support, ops burden, cost at your scale

### 5. Reranking deserves more than a clause

**Missing:** cross-encoders, hosted rerankers, late interaction.

**Why it matters:** retrieve-wide-then-rerank-narrow is the standard production shape and
usually the biggest single quality jump after hybrid search. The notes give it one sentence
inside an "other techniques" bullet list.

**Suggested note:** fold into `Hybrid-Search.md` or its own `Reranking.md`
- Bi-encoder (fast, precomputed) vs cross-encoder (slow, far more accurate) — why you can
  only afford the cross-encoder on the top ~50
- Hosted: Cohere Rerank. Open: BGE reranker
- ColBERT / late interaction as the middle ground
- The latency budget this adds, stated honestly

---

## P2 — production reality

The notes describe techniques. These are the things that decide whether the project ships.

### 6. Ingestion, beyond chunking

The notes cover chunk size, overlap and contextual embedding well. They do not cover
getting to the text in the first place, which is where most real projects stall.

- Document parsing: PDFs, tables, scans, OCR. Tables are the classic killer — chunking a
  table by character count destroys it
- Incremental updates and deletes: what happens when a source document changes
- Re-embedding when you switch model. The notes note this in passing ("changes to the
  embedding model require all documents to be re-setup") — it deserves a plan, not a clause
- Versioning the index so you can roll back a bad ingestion

### 7. Access control and multi-tenancy

Entirely absent, and it is the gap most likely to block a real deployment. Which chunks is
*this* user allowed to retrieve? Filtering at query time interacts directly with the ANN
recall problem in gap 3, and getting it wrong leaks documents across tenants.

### 8. Citations and attribution

Also absent, which is odd given the book's own pitch is "accurate, **explainable**,
context-aware". Covering: carrying chunk provenance through retrieval, getting the model to
cite, and verifying that the citation actually supports the claim.

### 9. Cost, latency and caching

- Embedding cost at ingestion vs query time
- Semantic caching, and why it is riskier than it looks
- Prompt caching for the large static parts of a RAG prompt
- **The cost of GraphRAG specifically**: an LLM call per chunk for entity extraction, plus
  a call per community summary. The notes describe the technique thoroughly and never once
  say what it costs to run

---

## P3 — framing and depth

### 10. Retrieval evaluation, separately from generation

The [RAGAS section](Essential-GraphRAG.md) covers answer quality — context recall,
faithfulness, answer correctness. There is nothing on evaluating *retrieval on its own*:
recall@k, precision@k, MRR, nDCG@k. Without those you learn that the answer is bad but not
whether retrieval or generation broke it. Also missing: how to build the golden dataset,
which is the actual hard part.

### 11. When *not* to reach for this

A session that only sells the technique is less useful than one that draws the line.

- Long context vs RAG: when does dumping the documents in the prompt just win
- When plain keyword search is enough
- When GraphRAG's indexing cost is not repaid — the notes explain the technique but never
  offer the "is this worth it" test

### 12. Cypher primer — and Cypher is not Neo4j-only

The [text2cypher section](Essential-GraphRAG.md) hands the audience a prompt template that
generates Cypher, for an audience that has likely never read Cypher. A few slides of
`MATCH (p:Person)-[:ACTED_IN]->(m:Movie) RETURN m.title` before that section would carry it.

Worth stating explicitly, because the notes imply otherwise: **Cypher is not a Neo4j-only
language.** It started at Neo4j, but was opened up as **openCypher** in 2015 and is
implemented by Memgraph, Amazon Neptune, and **Apache AGE** (a Postgres extension) among
others. RedisGraph also spoke it before being discontinued.

More importantly, **GQL** (ISO/IEC 39075:2024) is now a real ISO standard — the first new
ISO database language since SQL — and it is heavily derived from Cypher. Neo4j is steering
Cypher toward conformance.

The practical caveat: dialects genuinely differ, so a generated query is not automatically
portable, and most Cypher in the wild still runs on Neo4j. But for the session it means
text2cypher is a transferable skill rather than vendor lock-in — and Apache AGE makes a
Postgres-only demo possible if you would rather not stand up Neo4j.

### 13. GraphRAG has moved since the book

Microsoft's implementation gained **LazyGraphRAG** (defers the expensive indexing until
query time, dramatically cheaper) and **DRIFT search** (blends local and global) after the
book's cutoff. Worth a slide so the session is not describing a frozen snapshot.

---

## Corrections to the existing notes

Left as-is in the source notes — flagged here rather than silently edited.

| Note | Currently says | The issue |
| --- | --- | --- |
| [Vector Similarity Search](Vector-Similarity-Search.md) | "Embedding model: **the result of a semantic classification**" | Nothing is being classified. It is a trained encoder mapping text to a vector |
| [Vector Similarity Search](Vector-Similarity-Search.md) | "Cosine similarity: **0 = completely different, 1 = identical**" | Cosine ranges −1 to 1. 0 is orthogonal, −1 is opposite. Rare for text embeddings in practice, but as written it is wrong |
| [Vector Similarity Search](Vector-Similarity-Search.md) | "Euclidean distance: **content and intensity of the text**" | Vague, and it omits the useful part: on L2-normalized vectors Euclidean and cosine rank identically, so the choice only matters when you skip normalization |
| [Essential GraphRAG](Essential-GraphRAG.md) | "Communities are created using the **Louvain Algorithm**" | Microsoft's GraphRAG implementation uses *hierarchical Leiden*. Leiden fixes a known Louvain failure mode where communities can come out internally disconnected |
| [Essential GraphRAG](Essential-GraphRAG.md) | "**hypotethical question strategy**" | Worth naming its better-known sibling, **HyDE** (Hypothetical Document Embeddings), which embeds a generated *answer* rather than a generated question |

### Typos carried over verbatim from the export

`hypotethical` · `identift` · `carreer` · `statrment` · `informatuon` · `respind` ·
`approperiate` · "un the RAG app" · "The create the final answer"
