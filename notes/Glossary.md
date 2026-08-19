# Glossary

Plain-language definitions, ordered roughly by when they come up in the
[session](Session-Outline.md). Intended to be **handed out on paper at the start** — a room
new to the topic loses more people to undefined vocabulary than to difficult ideas, and a
sheet they can glance at costs nothing.

Deliberately informal. Precision is in the other notes.

## The basics

**LLM (Large Language Model)** — the thing that writes the answer. Learned from a very large
amount of text up to a cutoff date. Knows nothing about your company and will answer anyway.

**Hallucination** — a confident, fluent, invented answer. Not a malfunction; it is what the
model does when it lacks the facts, because nothing tells it to stop.

**Context / context window** — everything you put in front of the model for one question:
your question plus whatever documents you pasted in. It has a size limit, and you pay per
word of it.

**Prompt** — the full text sent to the model. In RAG it is assembled: instructions + the
retrieved chunks + the user's question.

**RAG (Retrieval-Augmented Generation)** — find the relevant documents, staple them to the
question, let the model answer from them. An open-book exam.

**Grounding** — an answer being traceable to a document you actually supplied, rather than
to the model's memory. The point of the whole exercise.

## Finding things

**Chunk** — a piece of a document, typically a few paragraphs. Documents get chopped up
because you retrieve pieces, not whole files. An index card.

**Chunking** — the chopping. How big, where to cut, and how much the pieces overlap.

**Embedding** — coordinates on a map of meaning. An embedding model reads text and produces
a long list of numbers; text with similar meaning gets nearby numbers.

**Embedding model** — the model that produces those coordinates. **Not** the model that
writes answers. There are two different models in every RAG system.

**Dimension** — how many numbers are in one embedding. Commonly 384 to 3072. More is
generally more precise and more expensive.

**Vector** — the list of numbers itself. Same thing as an embedding.

**Vector search / similarity search** — embed the question, return the chunks whose
coordinates are nearest. Matching on meaning rather than spelling.

**Cosine similarity** — the usual way of measuring "how near". Near 1 means very similar;
near 0 means unrelated.

**Vector store / vector database** — where the chunks and their coordinates live, and what
does the nearest-neighbour search. `pgvector` turns Postgres into one.

**Index** — the data structure that makes finding the nearest coordinates fast. It gives
*approximate* answers on purpose, trading a little accuracy for a lot of speed.

**Top-k** — how many chunks retrieval returns. `k=5` means the five nearest.

**Keyword search / full-text search / BM25** — the classic kind: matching actual words.
BM25 is the standard scoring method. Still unbeatable for exact codes, names and identifiers.

**Hybrid search** — running keyword and vector search together and merging the results,
because they fail on different things.

**RRF (Reciprocal Rank Fusion)** — the standard way to merge two ranked lists into one,
using positions rather than scores.

## Making it better

**Reranking** — after retrieval returns a shortlist, a slower and more careful model re-sorts
it. Usually the second biggest quality win.

**Query rewriting** — editing the user's question before searching, because the question as
typed is often a poor search query.

**Step-back prompting** — one kind of rewriting: broaden an over-specific question so it
matches more documents.

**Metadata / metadata filter** — the facts attached to a chunk (which document, whose CV,
what date) and restricting search to chunks matching them.

## The graph half

**Knowledge graph** — facts stored as a network: things (consultant, skill, project) and how
they connect (*has skill*, *worked on*). A drawing rather than prose.

**Entity** — one thing in that network. A person, a skill, a client.

**Relationship** — a labelled connection between two entities.

**Entity resolution** — noticing that `Wouter Van Schandevijl`, `W. Van Schandevijl` and the
email address are all one person, and merging them. Without it, counts are wrong.

**Cypher** — the query language for graph databases. Its queries look like little drawings
of the pattern you want. Not Neo4j-only, despite the association.

**text2cypher** — having an LLM write the Cypher query for a plain-English question.

**Neo4j** — the best-known graph database, and the one the book uses.

**GraphRAG** — RAG where the retrieval step queries a knowledge graph instead of (or as well
as) searching chunks. Answers *how many*, *which ones*, and *what is true across everything*
— the questions chunk retrieval cannot.

**Community** — a cluster of closely-connected entities found automatically in the graph.
GraphRAG summarizes each one, which is how it answers "what are the themes across
everything".

**Global search / local search** — GraphRAG's two modes. Global uses the community summaries
to answer broad questions; local starts from specific entities and follows their connections.

## Judging it

**Golden dataset / eval set** — questions paired with the answers or chunks that should come
back. The thing that lets you tell whether a change helped.

**Recall@k** — of the chunks that should have been found, how many made it into the top k.
The ceiling on everything downstream.

**RAGAS** — a Python library of RAG evaluation metrics.

**Faithfulness** — whether everything in the answer is actually supported by the retrieved
chunks, rather than invented alongside them.
