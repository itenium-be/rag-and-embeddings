# Vector stores

Fills gap 4 in [Gaps](Gaps.md). The notes never name a single product, and "where do the
vectors actually live" is the question the audience will take back to work.

## The opinion first

**If Postgres is already in your stack, start with `pgvector` and only leave when you can
name the reason.**

Most RAG corpora in a consulting context are tens of thousands of chunks, not billions. At
that size a dedicated vector database buys you very little and costs you a new service to
operate, back up, secure and keep in sync with the source of truth. Meanwhile your chunks
almost always have relational metadata — tenant, document, author, validity dates — and
joining that in SQL, in one transaction, against data that cannot drift out of sync, is
worth more than a faster ANN implementation.

The reasons to leave are real, just specific: corpus far beyond memory, sustained
high-QPS filtered search, or a need for built-in hybrid and reranking you would otherwise
build yourself.

## The menu

| Store | Shape | Why you would pick it |
| --- | --- | --- |
| **pgvector** | Postgres extension | Already there. HNSW + IVFFlat, `halfvec`/`bit`/`sparsevec` types, real transactions and joins |
| **pgvectorscale** | pgvector + DiskANN | When the corpus outgrows RAM but you want to stay in Postgres |
| **Qdrant** | Rust, self-host or cloud | Best-in-class filtered search, native quantization, sparse+dense in one collection |
| **Weaviate** | Self-host or cloud | Hybrid with fusion built in, module ecosystem |
| **Milvus** | Distributed | Genuine billion-scale, many index types, heaviest ops burden |
| **Chroma** | Embedded / local | Prototypes and notebooks. Great for a demo, not a deployment |
| **Pinecone** | Managed only | Zero ops, serverless. You are renting, and your data lives there |
| **Elasticsearch / OpenSearch** | Search engine | You already run it for logs; BM25 and RRF are native, which makes hybrid nearly free |
| **Redis** | In-memory | Already in the stack, latency-critical, corpus fits in RAM |
| **MongoDB Atlas / Azure AI Search** | Managed platform | The platform decision was made above your pay grade |
| **Neo4j** | Graph + vector index | The bridge to the second half of this session |

## Neo4j deserves its own paragraph

[Essential GraphRAG](Essential-GraphRAG.md) is a Neo4j book, and Neo4j has both a vector
index and a full-text index. That means the entities, the relationships, the source chunks
and their embeddings can live in one database — you can vector-search to find entry-point
entities and then traverse relationships from them in a single Cypher query.

That is exactly the local search pattern the book describes, and it is much less impressive
when it spans two systems with a network hop and a consistency problem in between. If the
session is going to end in GraphRAG, this is the honest argument for putting the vectors
in the graph store.

Cypher itself is not Neo4j-only — see gap 12 in [Gaps](Gaps.md) — but the vector-plus-graph
integration story is where Neo4j is genuinely ahead.

## How to choose

Ask these in order, and stop at the first one that decides it:

1. **Can it filter correctly at your selectivity?** See the trap in
   [Vector Indexes](Vector-Indexes.md). This eliminates more candidates than performance ever
   will, and it fails silently.
2. **Do you need multi-tenancy?** Per-tenant isolation is a first-class feature in some
   stores and a metadata field you must never forget in others. One is a security boundary,
   the other is a bug waiting to be written.
3. **Hybrid search built in, or do you fuse in application code?** See
   [Hybrid Search](Hybrid-Search.md).
4. **Who operates it at 3am?** A dedicated store is another thing to back up, upgrade,
   secure, and page someone about.
5. **Where does the data physically sit, and is that allowed?** For internal documents this
   frequently decides the whole architecture before any benchmark is run.
6. **Only then**: how fast is it, and how much does it cost at your scale.

Benchmarks are last on purpose. Every store on that list is fast enough for a corpus of a
few hundred thousand chunks. Almost none of the real decisions are about speed.

## For the session

**Not session one.** Session three material — see the parked list in the
[outline](Session-Outline.md). Beginners need to know a store exists; the comparison matters
only once someone is actually choosing one.

Resist the urge to build a feature matrix — it will be out of date before you present it and
nobody remembers a twelve-column table. Give them the opinion, the six questions, and the
Neo4j bridge. That is what they can act on.
