# Reranking

Fills gap 5 in [Gaps](Gaps.md). [Essential GraphRAG](Essential-GraphRAG.md) gives this one
clause inside a bullet list — "an algorithm reorders them based on relevance as an extra
pass using a more sophisticated model or scoring heuristics" — which is accurate and tells
you nothing about what to actually run.

Retrieve-wide-then-rerank-narrow is the standard production shape and usually the second
biggest quality jump after [hybrid search](Hybrid-Search.md).

## Why a second pass exists at all

The retriever's job is to be fast over millions of documents, which forces a compromise:
the query and the document are embedded **separately**, and the document's vector was
computed long before your query existed.

That is a **bi-encoder**, and it is why precomputation works — but it also means the model
never sees the query and the document *together*. It compresses each into a fixed vector and
hopes the relevant part survived.

A **cross-encoder** concatenates them:

```
[CLS] query [SEP] document [SEP]  →  transformer  →  relevance score
```

Now every query token can attend to every document token. It is dramatically more accurate,
and it is one full forward pass **per document**, with nothing precomputable. You cannot run
it over a million documents. You can easily run it over fifty.

Hence the pipeline:

```
query → retrieve top 50–150 (fast, approximate)
      → cross-encode all of them (slow, accurate)
      → keep top 5–10 → context
```

Cheap where the corpus is large, expensive only where the candidate set is small.

## What to use

- **Cohere Rerank** — the usual hosted default. One API call, takes a query and a list of
  documents, returns them scored. Trivially easy to bolt onto an existing pipeline.
- **BGE reranker** (`bge-reranker-v2-m3` and friends) — open weights, self-hostable,
  multilingual. The natural pick if the embeddings are already self-hosted.
- **Jina**, **mixedbread**, **Voyage** — same shape, hosted.
- **ColBERT / late interaction** — the middle ground. Stores a vector *per token* and scores
  with MaxSim. Much better than a bi-encoder, much faster than a cross-encoder, and the
  storage cost is an order of magnitude higher. Mention it; do not build the session on it.
- **LLM-as-reranker** — hand the candidates to an LLM and ask it to order them. Flexible,
  no extra infrastructure, slow and expensive. A reasonable stopgap, a poor destination.

## The knobs

**How many candidates to retrieve** is the real parameter, and it is a recall ceiling: the
reranker can only reorder what retrieval already found. If the right chunk is at rank 200
and you retrieve 50, no reranker saves you. Start at 50, raise it, and watch where quality
stops improving — that tells you whether your problem is retrieval or ranking, which is
worth knowing on its own.

**Latency** is the cost. A hosted reranker adds a network round trip plus scoring time on
top of retrieval, and it sits directly in the user's path. Reranking 50 candidates is
usually acceptable; reranking 500 usually is not. Measure it in your own pipeline rather
than trusting a vendor's number.

## Order matters after ranking too

Once you have your top chunks, **where you put them in the prompt affects the answer.**

The "lost in the middle" finding (Liu et al., 2023) is that models attend most reliably to
the beginning and end of a long context, and material buried in the middle gets used less —
even when it is plainly relevant.

So: put the best chunk first. If you are passing many chunks, some pipelines deliberately
place the strongest at the start *and* the end. And the more direct lever — pass fewer
chunks. Reranking well is what lets you drop from fifteen mediocre chunks to five good ones,
which improves the answer and cuts token cost at the same time.

This is the part people skip. Retrieval quality gets all the attention while context
assembly, the last step before generation, is left as "join the chunks with newlines".

## For the session

Part 4 of the [outline](Session-Outline.md), after hybrid search. This is **question 3** on
the scoreboard: "who is our strongest Kubernetes consultant?"

The demo that lands: the genuine Kubernetes expert — five years of it across three projects —
comes back at rank 12, buried under CVs that mention Kubernetes once in a tooling list. Show
the top 5 without reranking: plausible, on-topic, and the wrong people. Then rerank and watch
the expert jump to rank 1.

It makes the bi-encoder/cross-encoder distinction concrete in a way the architecture diagram
does not, and "our search returns people who mentioned it once instead of people who are good
at it" is a failure everyone in the room has hit.
