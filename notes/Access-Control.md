# Access control and multi-tenancy

Fills gap 7 in [Gaps](Gaps.md). Absent from the book notes entirely, and the gap most likely
to block a real deployment. With the BambooHR dataset in [Demo Data](Demo-Data.md) it is not
hypothetical: the people in the index are the people asking the questions.

## The core insight

**Your index is a copy of the data with different access controls than the source.**

BambooHR has a permission model — managers see their reports, HR sees everything, consultants
see themselves. The moment you export, chunk and embed, all of that is gone. What remains is
a flat pile of vectors where similarity is the only thing deciding what comes back.

Rebuilding those permissions on the retrieval side is not a nice-to-have. It is the thing
that makes the difference between a demo and something you can actually put in front of
colleagues.

## Filter inside the search, not after it

Attach the permission data to every chunk at ingestion time — the owning employee, the
department, a list of group IDs allowed to see it — and filter on it *during* retrieval.

This runs straight into the trap in [Vector Indexes](Vector-Indexes.md), and here the
consequences are worse than empty results:

- **Post-filtering** — retrieve `k`, drop the forbidden ones. Correct, but with a selective
  filter it commonly returns nothing, so the system looks broken for legitimate queries.
- **Naive pre-filtering** — can wreck HNSW traversal, degrading to brute force.
- **Filtered traversal** — what you want, and what Qdrant and pgvector's iterative scan do.

Whatever you choose, the filter must be **non-optional and applied server-side**. A filter
the caller passes in is a filter the caller can omit.

## Postgres row-level security is a real advantage

This is the strongest practical argument for the pgvector recommendation in
[Vector Stores](Vector-Stores.md): Postgres RLS lets you attach the policy to the *table*, so
the restriction holds no matter which query reaches it. Forgetting a `WHERE` clause stops
being a data leak.

Most dedicated vector stores give you namespaces or metadata filters instead — workable, but
the enforcement lives in your application code, which means every new code path is a fresh
opportunity to forget.

## Permissions drift

Whatever you index becomes stale the moment someone changes teams.

Store a **reference**, not a snapshot: put the group or department ID on the chunk and
resolve it to the current member list at query time. Materializing "these 14 people may see
this" into the chunk means every reorganisation silently grants or revokes access, and
nothing tells you.

For BambooHR the manager field is the natural source, and it is a hierarchy — "my reports,
and their reports" is a graph traversal. That is a nice bridge to the graph half of the
session: the same structure that answers *how many consultants report to X* also decides
*what X is allowed to retrieve*.

## Four ways it leaks

1. **Retrieval returns a forbidden chunk.** The obvious one, and the one filtering fixes.
2. **The answer launders it.** If a forbidden chunk reaches the prompt, filtering the
   *citation* afterwards does nothing — the content is already in the generated text.
   Filtering has to happen at retrieval, not presentation.
3. **Citations leak metadata.** Returning "3 documents matched but you cannot see them"
   discloses that they exist. Sometimes fine, sometimes exactly the leak.
4. **The embeddings themselves carry the text.** Embedding inversion research has shown that
   a meaningful amount of the original text can be reconstructed from its vector. Treat the
   vector store as holding the source data, not a safe hash of it — that decides where it is
   allowed to live and who gets database access.

## Multi-tenancy

Same problem with a harder boundary. Two options:

- **Namespace or collection per tenant** — strong isolation, no chance of a forgotten
  filter, but awkward with many small tenants and cross-tenant admin queries.
- **Shared index with a tenant filter** — efficient and flexible, and one missing filter
  crosses a boundary that must never be crossed.

For genuine tenant isolation, prefer the boundary the database enforces over the one your
code remembers.

## For the session

Part 9 of the [outline](Session-Outline.md), and worth promoting from a caveat to a demoed
feature.

The demo is small: run "who is on a performance improvement plan" as an admin, then as a
regular consultant, and show the second one returning nothing rather than a filtered
apology. Ninety seconds, and it is the most production-relevant thing in the session — this
is the question that decides whether the tool is allowed to exist, and almost no RAG talk
covers it.
