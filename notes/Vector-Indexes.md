# Vector indexes

Fills gap 3 in [Gaps](Gaps.md). [Vector Similarity Search](Vector-Similarity-Search.md)
correctly says the index finds *approximate* nearest neighbours and is "a tradeoff between
speed and accuracy" — this is what that tradeoff is actually made of, and which dials
control it.

## Start with no index

Brute force compares the query against every vector. It is **exact** — recall is 1.0 by
definition — and modern SIMD makes it far faster than people assume. For tens of thousands
of vectors it is genuinely the right answer, and for a few hundred thousand it is often
still fine.

Say this explicitly in the session, because the instinct is to reach for HNSW immediately
and then spend an afternoon tuning an approximation of an answer you could have had exactly.
**An index is a scaling decision, not a correctness one.** The only reason to add one is
that brute force got too slow.

## HNSW

The default everywhere, and the one to explain properly.

A **multi-layer navigable small world graph**. The top layer holds few nodes with long-range
links; each layer down is denser. Search enters at the top, greedily walks toward the query,
drops a layer, repeats. Long hops first, fine detail last — a skip list for metric space.

Three parameters:

| Parameter | When | Effect |
| --- | --- | --- |
| `M` | build | Edges per node. Higher = better recall, more memory, slower build |
| `ef_construction` | build | Candidate list size while building. Higher = better graph, slower build. Free at query time |
| `ef_search` | **query** | Candidate list size while searching. **This is your recall dial** |

`ef_search` is the one that matters day to day, because it is the only one you can change
without rebuilding. Raise it, recall goes up and latency goes up, monotonically. Tune it
against a labelled query set and pick your point on the curve — do not accept the default
without measuring.

The costs people forget: HNSW is **memory-resident** (vectors plus graph edges), and
**deletes are tombstones** — the graph does not heal, so a heavily-churned index degrades
until rebuilt.

## The rest, in a line each

- **IVF** — k-means the space into `nlist` cells, search only the `nprobe` nearest. Faster to
  build than HNSW, lower recall at equal speed, but much friendlier to updates.
- **IVF-PQ** — IVF plus product quantization. The classic billion-scale-on-a-budget combo.
- **DiskANN / Vamana** — graph index designed to live on SSD, for corpora that will not fit
  in RAM. `pgvectorscale` brings this to Postgres.
- **ScaNN** — Google's, with quantization tuned to preserve inner-product ranking.

## Quantization: where the bill goes down

Vectors are stored as float32 by default. That is usually more precision than the ranking
needs.

| Method | Size | Notes |
| --- | --- | --- |
| Scalar (int8) | 4× smaller | Nearly free in quality. Reach for this first |
| Binary (1 bit/dim) | **32× smaller** | Hamming distance is extremely fast. Needs rescoring |
| Product quantization | tunable | Subvector codebooks. Biggest savings, biggest quality cost |

Binary quantization sounds absurd and works better than it has any right to on
high-dimensional models (1024+), because sign patterns carry much of the signal. The pattern
that makes it viable is **oversample-and-rescore**: retrieve ~4× your `k` using binary
vectors, then re-rank those candidates with the full-precision vectors. You pay full
precision on a hundred vectors instead of a million.

Whatever you choose, **measure recall against the un-quantized index** on your own data. The
published numbers are for other people's corpora.

## Filtering: the trap

[Essential GraphRAG](Essential-GraphRAG.md) recommends "metadata-based contextual filters:
attach metadata and do a prefiltering" without the warning. Filters and ANN interact badly,
and this is where production RAG quietly breaks.

**Post-filter** — retrieve `k`, then drop non-matching results. Simple, and it silently
returns fewer than `k` results. With a selective filter (one tenant out of 500) it commonly
returns **zero**, and the pipeline reports "no relevant documents" for data that is sitting
right there.

**Pre-filter** — restrict to matching rows, then search. Exact, but naively it degrades to
brute force over the subset, and it can disconnect the HNSW graph: the walk has to traverse
*through* filtered-out nodes to reach its destination, and if they are gone it gets stranded
in a dead end.

**What good engines actually do** — filtered traversal: walk the full graph but only *keep*
matching candidates, with a planner that switches to brute force when the filter is
selective enough. Qdrant's filterable HNSW and pgvector's iterative scan are both this idea.

The practical rule for the session: **know which of the three your store does.** If it
post-filters and your filter is selective, you have a correctness bug waiting, not a
performance one — and it fails silently, which is worse.

## For the session

This is part 3 of the [outline](Session-Outline.md) — the shortest section, but the one
people ask about afterwards.

If you demo one thing here, demo the filter trap: same query, same data, add a selective
metadata filter, watch the results go empty. It takes ninety seconds and it is the kind of
bug people recognise from their own logs.
