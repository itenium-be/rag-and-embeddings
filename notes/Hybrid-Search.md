# Hybrid search

Fills gap 2 in [Gaps](Gaps.md). [Essential GraphRAG](Essential-GraphRAG.md) covers this in
one sentence — "combines exact keyword matches from a full text search index with the vector
search" — without naming BM25 or explaining how two ranked lists become one.

This is the highest value-per-minute topic in the session. It is a small amount of work and
it fixes the failure mode that makes demos look broken.

## Why dense retrieval alone is not enough

Embeddings encode *meaning*, which is exactly wrong for tokens that carry no meaning:

| Query type | What happens |
| --- | --- |
| `AZ-204` | Near-identical vector to `AZ-104` and `AZ-400`. The model sees "an Azure certification", not *which* one |
| Employee IDs, project codes, error codes | Same problem |
| Rare proper nouns — a consultant's surname, a client name | Underrepresented in training, poorly placed in the space |
| Acronyms and internal jargon | The model has never seen your company's vocabulary |
| Negation — "consultants **without** a security certification" | Embeddings are famously weak at negation; the vector for the negated sentence sits near the un-negated one |

Lexical search has the mirror-image weakness: it cannot match "car" to "automobile", or a
question to a paraphrased answer.

Neither is a superset of the other. **That is the argument for hybrid** — not "hybrid is
better", but "the two fail on disjoint query types".

## BM25 in one slide

BM25 is TF-IDF with two corrections, and both matter:

- **Term saturation (`k1`, ~1.2–2.0)** — the tenth occurrence of a word adds much less than
  the second. Raw TF-IDF lets a keyword-stuffed document dominate; BM25 does not.
- **Length normalization (`b`, ~0.75)** — long documents contain more of every term, so
  their term counts get discounted relative to the average document length.

That is genuinely all the audience needs. It is decades old, it needs no GPU, it needs no
training, and it still wins outright on exact-identifier queries.

## Reciprocal Rank Fusion

You now have two ranked lists with **incomparable scores** — a cosine similarity of 0.83 and
a BM25 score of 14.2 have no common ground, and BM25 scores are unbounded and corpus-
dependent, so you cannot even normalize them reliably across queries.

RRF sidesteps this entirely by **throwing the scores away and using only the ranks**:

```
score(d) = Σ  1 / (k + rank_i(d))
          lists i containing d
```

with `k ≈ 60` by convention. Rank 1 contributes 1/61, rank 2 gives 1/62, and so on.

Three properties make it the default:

- **No normalization, no tuning.** There is no weight to get wrong.
- **`k` damps the top.** Without it, rank 1 would dominate rank 2 far too heavily. With
  k=60 the top ranks are close together, so a document that both retrievers rank *decently*
  beats one that a single retriever loves.
- **Agreement is rewarded.** Appearing in both lists is worth more than topping one.

The last point is the actual magic. RRF is a voting scheme, and consensus between two
independent retrievers is a strong relevance signal.

```python
def rrf(ranked_lists, k=60):
    scores = {}
    for lst in ranked_lists:
        for rank, doc_id in enumerate(lst, start=1):
            scores[doc_id] = scores.get(doc_id, 0) + 1 / (k + rank)
    return sorted(scores, key=scores.get, reverse=True)
```

That is the whole algorithm — worth showing on a slide precisely because people expect
something harder.

### The alternative, and why it is fiddlier

Weighted score fusion — `α · dense + (1−α) · sparse` — can beat RRF *if* you tune it. But it
requires normalizing both score distributions (min-max over what window? z-score over which
corpus?), and the right `α` differs per query type. You are now tuning two things instead of
zero. Start with RRF; move to weighted fusion only when you have the eval set from gap 10 to
prove it helps.

## Learned sparse, briefly

**SPLADE** and friends sit between the two worlds: a transformer predicts a weight for every
vocabulary term, including terms not literally present, producing a sparse vector that an
inverted index can serve. You get synonym expansion with lexical-style exact matching.

Mention it, do not demo it. It needs specific index support and the operational story is
worse than "BM25 + dense + RRF", which gets you most of the benefit.

## What this looks like in practice

Most stores now ship hybrid, so this is rarely something you implement yourself:

- **Elasticsearch / OpenSearch** — BM25 natively, HNSW alongside, RRF built in
- **Weaviate** — hybrid query with a fusion strategy parameter
- **Qdrant** — sparse and dense vectors in one collection, server-side fusion
- **Postgres** — `pgvector` plus `tsvector`/`ts_rank`, fused in application code, or
  ParadeDB for real BM25

## For the session

This fixes **question 2** on the scoreboard in the [outline](Session-Outline.md).

Ask "who has the AZ-204 certification" and dense retrieval hands back the AZ-104 and AZ-400
people — confidently and fluently, which is what makes it a good scare, and which is exactly
the ~0.99 similarity you showed in part 1. Then add BM25 and RRF and watch it land on the
right consultants. Roughly fifteen lines of change for the most visible quality jump of the
whole session.
