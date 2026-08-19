# Embedding models

Fills gap 1 in [Gaps](Gaps.md). Depth behind
[Vector Similarity Search](Vector-Similarity-Search.md), which covers the search side but
treats the model itself as a paragraph.

## What the vector actually is

Not "the result of a semantic classification" — nothing is being classified. An embedding
model is a **trained encoder**:

1. Tokenize the text.
2. Run it through a transformer encoder, producing one vector *per token*.
3. **Pool** those into a single vector — either the `[CLS]` token's output, or (more common
   now) the mean of all token vectors.
4. Usually L2-normalize the result.

The interesting part is step 3's training. The encoder is trained **contrastively**: show it
pairs that should be close (a question and its answer, a title and its body) and push those
together, while pushing everything else in the batch apart. That "everything else in the
batch" is the trick — in-batch negatives make training cheap, and mining *hard* negatives
(plausible-looking wrong answers) is what separates a good model from a mediocre one.

So the geometry is not a fact about language. It is a fact about **what pairs the model was
trained to consider similar.** That is why a model trained on web Q&A can be poor on legal
clauses, and why "just use the top of the leaderboard" is not a strategy.

## Symmetric vs asymmetric, and the prefix gotcha

RAG search is **asymmetric**: a short question has to match a long passage. They are
different kinds of text and several models want to know which one you are handing them.

- **E5** models expect literal `query: ` and `passage: ` prefixes.
- **BGE** wants an instruction prefix on the query only.
- **Cohere** takes an `input_type` parameter (`search_query` vs `search_document`).

Forget this and quality drops noticeably while everything still *appears* to work — no
error, just worse results. It is the single most common silent misconfiguration in a RAG
pipeline, and worth a slide of its own.

## The lineup

| Model | Dims | Notes |
| --- | --- | --- |
| OpenAI `text-embedding-3-small` | 1536 | The sensible default. Cheap, ~8k token input |
| OpenAI `text-embedding-3-large` | 3072 | Better, several times the price |
| Cohere `embed-v3` family | 1024 | `input_type` built in; native int8/binary output |
| Voyage | varies | Domain variants — code, law, finance |
| **BGE** / **E5** / **GTE** | 384–1024 | Open weights, self-hostable, genuinely competitive |
| `all-MiniLM-L6-v2` | 384 | The old sentence-transformers workhorse. Tiny and fast |
| `nomic-embed-text`, Jina | 768+ | Open, long-context variants |

Verify current model names and pricing before the session — this part of the ecosystem moves
faster than any note can track. The last time I checked, the small OpenAI model was roughly
an order of magnitude cheaper per token than the large one, which matters far more at
ingestion time than at query time.

**Self-hosting is a real option.** A 384-dim open model on a modest GPU embeds a corpus for
the cost of the electricity, and removes the "we cannot send documents to a third party"
conversation entirely. For a lot of internal-document use cases that objection decides the
architecture before quality does.

## MTEB, and how to use it honestly

[MTEB](https://huggingface.co/spaces/mteb/leaderboard) is the standard leaderboard —
retrieval, classification, clustering, semantic similarity. Its retrieval half is largely
BEIR, which your notes already reference via the RavenDB quote.

Use it to build a **shortlist**, never to pick a winner. Leaderboard positions are separated
by fractions of a point, models are increasingly tuned against the benchmark, and none of
those datasets are your CVs. Take three plausible models, run them against fifty of
your own labelled queries, and pick from that. That evaluation is the same golden-set work
described in gap 10 — doing it once serves both purposes.

## Dimensions, cost, and Matryoshka

Dimension count drives storage and query cost linearly: 1M vectors at 1536 dims in float32
is roughly 6 GB before any index overhead. At 384 dims it is 1.5 GB.

**Matryoshka Representation Learning (MRL)** trains the model so that the *prefix* of a
vector is itself a usable embedding. OpenAI's `text-embedding-3` models support this via a
`dimensions` parameter — ask for 512 of the 1536 and you get a coherent 512-dim vector, no
re-embedding required. Renormalize after truncating.

This is a genuinely useful lever: it lets you trade recall for cost *after* you have already
embedded everything, which is otherwise the most expensive decision to reverse.

## Normalization, and why the metric question is mostly fake

Your notes list cosine and Euclidean as alternatives. On **L2-normalized vectors they rank
identically** — the relationship is exact:

```
||a - b||² = 2 - 2·cos(a, b)
```

Euclidean distance is a monotonic function of cosine similarity, so the sorted order is the
same. And once normalized, cosine *is* just the dot product, which is why most stores
normalize on write and use dot product internally — it is the cheapest of the three.

The choice only matters when you deliberately keep magnitude, which for text embeddings you
almost never do.

Also worth correcting from the current note: cosine ranges **−1 to 1**. Zero means
unrelated, not "completely different"; −1 means opposite. Modern text embedding models
rarely produce negative similarities in practice, but the stated range is wrong.

## Practical constraints to mention

- **Input token limits** (~8k for the OpenAI models, less for many open ones). Most APIs
  silently truncate rather than erroring — so an oversized chunk gets embedded as its first
  half, and you never find out.
- **Batch your ingestion calls.** One request per chunk is slow and rate-limit-prone.
- **Re-embedding is a migration.** Changing model means reprocessing the entire corpus, and
  you cannot mix vectors from two models in one index. Plan for it before you need it.
- **Multilingual**: if the corpus is Dutch/French/English, use a multilingual model rather
  than embedding each language separately.
- **Multimodal**: CLIP and SigLIP put images and text in one space. Worth thirty seconds so
  people know it exists.
