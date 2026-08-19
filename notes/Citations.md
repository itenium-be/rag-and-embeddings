# Citations and attribution

Fills gap 8 in [Gaps](Gaps.md). Absent from the book notes, which is odd given the book's own
pitch is "accurate, **explainable**, context-aware GenAI applications". Citations are the
explainable part.

## Why this is the trust mechanism

Nobody verifies every answer. But whether an answer *can* be verified changes how people use
the system: a cited answer gets spot-checked occasionally and trusted in between, while an
uncited one is either trusted blindly or not used at all. Neither of those is what you want.

For the consultant dataset this is concrete. "Three consultants have AZ-204" is a claim.
"Three consultants have AZ-204 — *[CV: A. Janssens, p2]*, *[BambooHR training record]*,
*[CV: M. Peeters, p1]*" is a claim someone can check in ten seconds, and will, the first
time it looks wrong.

## Provenance has to survive the whole pipeline

The plumbing is the boring part and the part that breaks. Every chunk needs to carry, from
ingestion all the way to the rendered answer:

- a stable chunk ID
- the source document ID, and a title a human recognises
- a location — page number, section heading, or character offsets
- a link that opens the source

Most pipelines lose this at the join step, where retrieved chunks get concatenated into one
prompt string and the boundaries disappear. Number the chunks in the prompt instead, and
keep a lookup from number back to source:

```
[1] (CV: A. Janssens, p2) ...chunk text...
[2] (BambooHR training records) ...chunk text...
```

Then ask for citations by number in the system prompt. That mapping is what lets you turn
`[2]` in the output back into a real link.

## Verify the citation, do not just render it

**A citation is not evidence of grounding.** Models cite plausibly and wrongly — pointing at
chunk 2 for a claim that chunk 2 does not support, or citing a real chunk for a detail it
invented. Rendering that unverified is worse than no citation, because it manufactures
confidence.

The check is the faithfulness idea already in the book notes, applied per claim: decompose
the answer into atomic statements, and for each one ask whether the cited chunk actually
supports it. It is the same decomposition RAGAS uses — see [Evaluation](Evaluation.md) — so
building it once serves both citation verification and your eval harness.

At minimum, validate cheaply: check that every cited number refers to a chunk that was
actually retrieved. Models occasionally cite `[7]` when you passed five chunks.

## Some APIs do this natively

Rather than prompting for citation markers and parsing them out, several providers now
support citations as a first-class feature. On the Claude API you enable
`citations: {enabled: true}` on each document content block; the response comes back split
into text blocks, where cited blocks carry a `citations` array giving the quoted source text,
which document it came from, and its location — character offsets for text, page numbers for
PDFs.

The advantage over prompt-and-parse is that the cited span is returned as **data** rather
than as markup inside prose you have to regex. If your generation step already passes
documents, prefer the native mechanism.

## Design the failure case

The most valuable thing a citing system does is **decline**. If retrieval returns nothing
relevant, the right answer is "I do not have information about that" with no citation — not
a fluent paragraph assembled from the closest five chunks.

This is worth stating in the session because it inverts the usual instinct. An answer with no
citation should be treated as a bug, and a system that says "I do not know" on genuinely
unanswerable questions is more useful than one that never does, not less.

## For the session

Part 5 of the [outline](Session-Outline.md) — it answers "how do I know it isn't making this
up?", which someone will have been waiting to ask since the invented answer in part 0. That
makes it one of the few advanced-sounding topics that genuinely belongs in a first session.

The demo: ask a question the corpus genuinely cannot answer, and show the uncited confident
paragraph. Then show the same query with citations and a refusal path. The contrast lands
harder than any accuracy metric.
