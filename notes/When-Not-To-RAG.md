# When not to reach for this

Fills gap 11 in [Gaps](Gaps.md). The book notes describe every technique and never draw the
line. A session that only sells the technique is less useful than one that says where it
stops paying.

This is also the most credible way to end. A talk that concludes "and here is when not to do
any of it" gets trusted on everything that came before.

## Long context sometimes just wins

Current models take very large contexts. If the entire corpus fits, RAG's whole reason for
existing — you cannot fit the documents in the prompt — no longer applies.

For the consultant dataset this is a live question, not a theoretical one. Fifty CVs is
plausibly a few hundred thousand tokens. That fits. And a model reading all of them sees
things no retriever will ever surface, because it never has to decide what is relevant first.

The tradeoffs, honestly:

- **Cost** — you pay for the whole corpus on every query instead of five chunks. Prompt
  caching (see [Cost and Caching](Cost-And-Caching.md)) changes this maths substantially,
  since a static corpus is exactly the stable prefix caching is built for.
- **Latency** — more input tokens, slower first token.
- **Attention dilution** — "lost in the middle" (see [Reranking](Reranking.md)) applies here
  too; a needle in 300k tokens is genuinely harder than one in 3k.
- **It does not scale** — this works at hundreds of documents, not hundreds of thousands.

**The pragmatic move**: try long context first as a quality baseline. If dumping everything
in the prompt answers your five questions and RAG does not, you have learned something
important about your retrieval before building any of it.

## Keyword search is sometimes enough

If users search for identifiers, names and exact phrases, BM25 alone answers them — no
embedding bill, no vector store, no re-embedding migration, no ANN recall tuning.

The honest test: take twenty real queries and run them through plain full-text search. If
most are answered, the remaining gap may not justify the infrastructure. See
[Hybrid Search](Hybrid-Search.md) — it is worth knowing that half of "hybrid" often does most
of the work.

## Structured questions want a database

This is really the book's own argument, stated from the other side. "How many consultants
are available in October" is a `SELECT COUNT(*)`. Routing it through chunk retrieval is a
worse way to answer a question that BambooHR can already answer exactly.

The book's answer is text2cypher over a knowledge graph, which is right when the structure
is scattered across unstructured sources. But when the data is *already* in a well-modelled
database, text2sql against the database beats extracting entities into a graph and querying
that. Do not build a knowledge graph to recover structure you never lost.

## GraphRAG specifically

The indexing cost is real (see [Cost and Caching](Cost-And-Caching.md)) and it recurs on
every rebuild. Ask three questions before committing:

1. **Do people actually ask global questions?** GraphRAG's distinctive win is "what are the
   themes across everything". If nobody asks that, you are paying for a capability that is
   never used.
2. **Is the corpus stable?** Rebuild cost multiplied by change frequency is the real number.
3. **Is the entity structure discoverable?** GraphRAG extracts entities from unstructured
   text. If your entities are already fields in a system of record, extract from there —
   cheaper, deterministic, and no entity resolution problem.

For the itenium dataset the answer is interestingly mixed: BambooHR gives you the entities
for free, so the expensive extraction step only needs to run over the CVs and project
sheets. That is a good outcome, and it is worth showing the reasoning rather than just the
conclusion.

## The general test

**Does the question need retrieval, or does it need structure?**

Retrieval finds passages that resemble the question. It is the right tool when the answer
exists as prose somewhere and the problem is locating it. It is the wrong tool when the
answer must be computed, counted, filtered or aggregated across many records — no amount of
chunking makes a retriever into an aggregation engine.

Most disappointing RAG systems are the second question asked of the first tool.

## For the session

Part 9 of the [outline](Session-Outline.md), and the closing note.

Resist ending on a victory lap. The room will remember "vectors cannot count" and "try long
context first" longer than they will remember the RRF formula, and both make them better at
choosing than at implementing — which is the more valuable skill.
