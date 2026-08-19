# GraphRAG since the book

Fills gap 13 in [Gaps](Gaps.md). [Essential GraphRAG](Essential-GraphRAG.md) describes
Microsoft's implementation as of writing. It has moved since, and mostly in the direction of
the cost complaint in [Cost and Caching](Cost-And-Caching.md) — worth a slide so the session
is not presenting a frozen snapshot.

## What the book describes

The two-stage pipeline: extract entities and relationships from every chunk, detect
communities, summarize each community, then answer either by **global search** (map/reduce
over community summaries) or **local search** (vector-find entities, traverse outward, rank).

That is still accurate and still the right mental model. What follows are refinements, not
replacements.

## LazyGraphRAG

The direct answer to the indexing bill. Standard GraphRAG does all the expensive LLM work up
front — a call per chunk to extract, a call per community to summarize — whether or not
anyone ever asks a question that needs it.

LazyGraphRAG defers that. It builds a much cheaper index using classical NLP for the
extraction step and no upfront summarization at all, then does the LLM work **at query
time**, only for the part of the graph the question actually touches.

The tradeoff moves cost from indexing to querying, which is the right direction when the
corpus is large and the global questions are rare — the exact situation described in
[When Not To RAG](When-Not-To-RAG.md). Microsoft reported comparable answer quality at a
small fraction of the indexing cost.

For the itenium dataset this matters less than it might, because the corpus is small and the
entities largely come free from BambooHR. But it is the right thing to reach for when
someone in the room asks "what about our 40,000 document SharePoint".

## DRIFT search

The book presents global and local search as a choice. In practice many real questions are
neither purely one nor the other — "which skills are we short on **in the cloud team**" needs
the global thematic view *and* a specific local entry point.

DRIFT (Dynamic Reasoning and Inference with Flexible Traversal) blends them: start from
community summaries for the broad framing, then follow up with local traversal to refine,
iterating as needed. It behaves more like the agentic loop the book describes in its Agentic
RAG section than like a single retrieval pass.

Worth one slide, mainly so people know the global/local split is a starting taxonomy rather
than a fixed menu.

## A correction while you are here

The book notes say communities are built with the **Louvain algorithm**. Microsoft's
implementation uses **hierarchical Leiden**.

The distinction is worth thirty seconds because it is a genuine improvement, not a rename:
Louvain can produce communities that are internally *disconnected* — a cluster whose members
are not actually linked to each other, which is exactly what you do not want when the next
step is "summarize this community as a coherent topic". Leiden guarantees connected
communities, and its hierarchical form is what gives GraphRAG the multi-level community
structure the book describes.

## Where the field is going

The broader trend worth naming: **the graph is becoming one retriever among several**, rather
than the architecture. That is already the book's own Agentic RAG chapter — a router, several
retrievers, an answer critic — with the graph as one of the retrievers alongside vector
search and text2sql.

That framing ages better than "GraphRAG vs vector RAG", which is the framing the room will
arrive with. The useful takeaway is not that graphs beat vectors, but that questions have
shapes, and a serious system routes each shape to the retriever that fits it.

## For the session

**Session two material** — the GraphRAG session that the [outline](Session-Outline.md) sets
up. Place it after the global search demo, alongside the cost discussion.

Keep it short — this is context, not content. One slide: "the book is accurate; here is what
happened next, and it is mostly about making it cheaper." Then the Leiden correction, which
costs nothing and makes the rest of your material more credible.
