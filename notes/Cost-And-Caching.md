# Cost, latency and caching

Fills gap 9 in [Gaps](Gaps.md). The book notes describe every technique without ever saying
what any of it costs — including GraphRAG, whose indexing bill is the largest number in the
whole architecture.

## Where the money goes

Split it in two, because they behave completely differently.

**Ingestion — one-off, proportional to corpus size.** Embedding a corpus is usually far
cheaper than people expect: embedding models are priced roughly an order of magnitude below
generation models, and CVs plus BambooHR records is a small corpus. This is rarely the
problem.

**Query time — recurring, proportional to usage.** One embedding call for the query (tiny),
retrieval (essentially free), an optional reranker call, and then generation with several
thousand tokens of retrieved context. **Generation dominates**, and it dominates because of
the context you stuff into it.

Which gives the most useful cost lever in RAG: **retrieve fewer, better chunks.** Reranking
well (see [Reranking](Reranking.md)) lets you drop from fifteen mediocre chunks to five good
ones — better answers *and* a third of the input tokens. Quality and cost point the same
direction here, which is rare enough to point out.

## GraphRAG is the expensive one

Say this plainly in the session, because the book does not.

Microsoft-style GraphRAG indexing costs **one LLM call per chunk** for entity and
relationship extraction — more if you run the self-reflection iterations the book recommends
to catch missed entities — plus **one call per community** for summarization, across every
level of the hierarchy.

That is not a rounding error. It is generation-model pricing applied to your entire corpus,
several times over. For a few hundred CVs it is an afternoon and a modest bill. For a large
document estate it is a budget line, and it recurs every time you rebuild.

The honest framing: GraphRAG buys you question types that vector RAG simply cannot answer
(questions 4 and 5 on the [outline](Session-Outline.md) scoreboard). Whether that is worth
the indexing cost depends entirely on how often anyone asks those questions. Sometimes the
answer is no, and a session that says so is more credible than one that does not.

## Prompt caching

A RAG prompt is mostly stable — a long system prompt, format instructions, few-shot
examples — with a small variable part at the end. Prompt caching bills the stable prefix at a
steep discount on repeat requests.

The mechanics that matter:

- It is a **prefix match**. Any byte change anywhere in the prefix invalidates everything
  after it. Order is tools → system → messages, so stable content goes first and volatile
  content (the user's question, retrieved chunks, timestamps) goes after the last cache
  breakpoint.
- On the Claude API, cache reads cost about **0.1×** normal input price, while writes cost
  **1.25×** at the default 5-minute TTL (or 2× for the 1-hour TTL). At 5 minutes, two
  requests already break even.
- **Verify it is working.** Check `cache_read_input_tokens` on the response. If it is zero
  across repeated requests, something in your prefix is changing — a `datetime.now()` in the
  system prompt and non-deterministic JSON key ordering are the classic culprits.

The catch specific to RAG: **retrieved chunks are different every query**, so they cannot be
cached. What caches well is the system prompt, the output format instructions, and any
few-shot examples — which for a well-built RAG prompt is a substantial share of the tokens.

## Semantic caching, and why to be careful

The idea: embed the incoming question, and if it is close enough to a previous question,
return the stored answer.

It is riskier than it looks. "How many consultants are available in October?" and "How many
consultants are available in November?" are extremely close in vector space and have
different answers. So are questions differing only by a name or a negation — the same
weakness described in [Hybrid Search](Hybrid-Search.md), now deciding whether to serve a
stale answer.

If you use it: set the threshold high, exclude anything time-sensitive or personalised, and
key the cache by user where permissions differ (see [Access Control](Access-Control.md) — a
shared cache is an access-control bypass with extra steps).

## Latency budget

Roughly, in the user's path:

| Step | Order of magnitude |
| --- | --- |
| Embed the query | tens of ms |
| Vector search | single-digit to tens of ms |
| Rerank ~50 candidates | ~100–300 ms |
| Generation | seconds, dominated by output length |

Generation dominates, so **stream the response** — perceived latency drops far more than any
retrieval optimisation will buy you. Optimising a 20 ms search while the user waits four
seconds for tokens is the wrong end of the problem.

## Measure tokens properly

Do not estimate with a character count or another vendor's tokenizer. Use the provider's
token-counting endpoint — on the Claude API that is `messages.count_tokens`. Chunk sizes are
specified in characters and billed in tokens, and the ratio varies enough by language and
content that guessing produces budget surprises.

## For the session

**Session three material** — see the parked list in the [outline](Session-Outline.md). The
GraphRAG cost point belongs in session two instead, right after the global search demo
lands: that is the moment the room is most impressed, and therefore the moment to say what
it costs.
