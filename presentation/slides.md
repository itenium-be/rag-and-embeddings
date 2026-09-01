---
theme: ./theme
title: RAG and Embeddings
subTitle: Vector RAG from the ground up
transition: fade
session-time: 60min
track: ai
type: Theoretical
first: 2026-09-01
aspectRatio: 16/10
---

# RAG
# Embeddings

::image::

![](./images/cover-art.webp)

---
layout: two-col-image-text
image: ./images/tech-lunch.webp
h1:
  type: braces
  color: primary
  position: all
---

# Tech Lunch

## 17 september · 12u–13u

::content::

<TechLunch />

---
layout: full
---

<TheAlignmentProblem />

---
layout: full
---

<MoreSessions />

---
layout: agenda
items:
  - RAG
  - Embeddings
  - Use Case
---

---
layout: section
background: rag.webp
---

# RAG

::subtitle::

Retrieval Augmented Generation

---
layout: default
clicks: 3
h1:
  type: braces
  color: primary
  position: all
---

# RAG
## RAG What?

<RagBox :clicks="$clicks" />

---
layout: default
clicks: 6
---

# RAG

## An Example

<WithoutRag :clicks="$clicks" />

---
layout: default
clicks: 6
---

# RAG

## Adding the answer to the prompt

<WithRag :clicks="$clicks" />


---
layout: default
clicks: 2
h2:
  type: dot
  color: primary
  position: end
---

# Use Case

## Consultants asking itenium anything

<UseCase :clicks="$clicks" />

---
layout: section
background: embeddings.webp
---

# Embeddings

::subtitle::

Search PDFs... How?



---
layout: default
clicks: 5
---

# Embeddings

## Just paste them all in?

<ContextWindow :clicks="$clicks" />

---
layout: default
clicks: 5
h1:
  type: hash
  color: muted
  position: start
---

# Chunking

## Split into pieces

<Chunking :clicks="$clicks" />

---
layout: default
clicks: 3
---

# Embedding

## Chunks to vectors

<RealVector :clicks="$clicks" />

<!--
384 is the network's width - 12 attention heads of 32 - not a decision about meaning.
The vector is the mean-pooled last hidden state, so it comes out exactly as wide as the
model is inside. e5 small/base/large = 384/768/1024; OpenAI's are 1536 and 3072. The
cost is linear: 384 buys 3.37 MB for the corpus and 842k multiply-adds per question,
1536 would be four times both for somewhat finer distinctions.

No single dimension means "is about Kubernetes" - meaning is spread across all 384,
which is why these numbers look like noise and only the dot product says anything.

We picked this model for being multilingual, not for being small: a Dutch question has
to reach an English CV. Foundations.md still says 1536 - that is OpenAI's number and
wrong for this deck.
-->

---
layout: default
clicks: 3
---

# Embeddings

## A map of meaning

<MeaningMap :clicks="$clicks" />

<!--
Nobody placed these points. The map is *learned* from public training text, not
discovered - which is exactly why it is poor at anything only we say. Project
codenames, "PS-3 formulier", an internal tool name: the model never saw them, so it
puts them somewhere arbitrary and near stops meaning similar. Same reason AZ-204
lands next to AZ-104 - question 2, fixed in part 4 by keyword search, which needs no
map at all.

What it *is* good at is the ordinary language of the trade, in both languages: the
Dutch question above reaches an English CV because one multilingual model drew both.
-->

---
layout: default
clicks: 7
h2:
  type: slashes
  color: muted
  position: end
---

# Embeddings

## Comparing two vectors

<DotProduct :clicks="$clicks" />

<!--
The `.npy` file holds no index and no notion of similarity - it is a header and 3.2 MB
of raw floats. The comparison is one line: `vectors @ query_vector`, then sort. 2194 dot
products, sub-millisecond, no clever data structure anywhere.

**Why this dot product is already the cosine.** The definition is
`cos = (a·b) / (|a| x |b|)`. `|a|` is Pythagoras over all 384 numbers - the square root
of the sum of their squares - so it says how far the point sits from the origin and
nothing about which way it points. The encoder normalises: every vector is divided by
its own `|a|`, and all 2194 come out at exactly 1.0000. Both denominators are 1, the
division does nothing, and the sum they just watched *is* the cosine.

Three things that buys us. No normalising step at query time - `vectors @ query_vector`
and nothing else. A score bounded to -1..1 for free. And no magnitude bias: un-normalised,
a vector that merely happens to be bigger outranks a smaller one whatever direction it
points in.

**Saying the bar out loud.** Cosine runs -1..1, so you expect a good match near 1 and an
unrelated pair near 0. That is not what happens. Across all 2 405 721 pairs the *lowest*
score in the company is 0.661 - a paragraph of Michael Dumortier's CV against Nicolas
Legrand's credit balance, two texts with nothing in common - and the average pair is
0.812. Our correct match scored 0.887. That is what right looks like: barely above the
noise.

So the number means nothing on its own. 0.887 is not "89% relevant", and there is no
threshold to set - you sort and take the top few, which is exactly what the code does.
It is also why the scores look so compressed on the hybrid slide: 0.844 against 0.831 is
a real gap, it just does not look like one.

Why so compressed: everything here was written by people, at one company, about work, in
two related languages. The model puts all human prose in one neighbourhood - differences
are relative, never absolute.

The axis starts at 0.661 because nothing is below it. The box is the middle 98%, so 0.73
to 0.93 is where practically everything sits; the whiskers are single pairs out of 2.4
million. And the top end, 0.999, is two BambooHR rows for the same person differing by a
single date. When near-identical records score that high, retrieval cannot separate them
- which is why "hoeveel credits heeft Simon nog" is doomed however good the search gets.
-->

---
layout: default
clicks: 9
---

# Embeddings

## The whole pipeline

<Pipeline :clicks="$clicks" />

---
layout: default
clicks: 8
---

# Retrieval

<QueryPipeline :clicks="$clicks" />

<!--
The pipeline slide showed retrieval as one box. This is that box.

Vector search is what we built and it is one option of several. Retrieval only has to
put the right context in the prompt - it does not have to be a similarity search. An API
call against BambooHR answers "who is free in October" properly; a SQL `count` answers
"how many" properly. Neither needs an embedding.

What decides between them is the agent box at the top, and that is the whole of session
2 - a model that picks the retriever, runs it, and checks its own answer. Today it is a
picture, not code: everything below the fan is vector search only.

The line worth landing: the model never sees your documents. It sees whatever retrieval
put in the prompt, and nothing else. Every failure for the rest of the session is a
retrieval failure, not a model failure.

The bottom row is not more retrievers - the fan never points at it. It is the three
things wrapped around the whole picture that we never get to. Access control: the same
question asked by two people should not return the same chunks, and with this dataset
that is not theoretical - session 3. Answer critic loop: a second pass that reads the
answer against the context it was given, and sends retrieval round again when it does
not hold up - session 2. Evaluation: you will change chunk size, or the embedding model,
or add a reranker, and "it feels better" is not an answer. A scored set of questions is.
-->

---
layout: default
clicks: 4
---

# Embeddings

## Five questions

<Scoreboard :clicks="$clicks" />

---
layout: break
---

# ☕ Break

::timer::

<Timer minutes="10" />

::image::

![](./images/cover-art.webp)


---
layout: default
clicks: 4
h2:
  type: semicolon
  color: muted
  position: end
---

# Making it work

## Hybrid search

<HybridSearch :clicks="$clicks" />

<!--
Two retrievers that fail on disjoint query types. `AZ-900` carries no meaning, so the
vector lands next to every other Azure certification and the question's Dutch prose -
"halen", "certificaat" - drags in the hospitalisatie folder instead. BM25 has never
heard of meaning and gets it right by spelling.

RRF throws the scores away - a cosine of 0.83 and a BM25 of 10.06 have no common
ground - and votes on ranks alone. Jos Van Loock is 12th on one list and 9th on the
other and ends up 4th; Thomas Janssens is BM25's number one and drops out of the top
five, because the vectors never saw him. Agreement is the signal.
-->

---
layout: default
---

# What we left out

| Technique                  | What it does                                                     | Why not today      |
| -------------------------- | ---------------------------------------------------------------- | ------------------ |
| Hypothetical questions     | Index a generated *question* per chunk, then match question to question | An ingest-time variant of what we did |
| Parent document retriever  | Retrieve the small chunk, hand the model the whole section around it   | Needs a failure we do not have |
| Metadata filters           | Constrain by source, person or date *before* ranking               | Session 3 — it is really access control |
| Router, agents, critic     | Let a model pick the retriever, then check its own answer          | Session 2 |
| Entity resolution          | Decide that `Gaëtan Boey` and `Gaetan Boey` are one person         | Session 2 |

<br>

That last one is not hypothetical: **36 CV names, 43 HR names, 29 that match.**
Seven colleagues are unjoinable across two systems because of an accent, a capital
and an apostrophe.

---
layout: socials
---

---
layout: source
source: itenium-be/rag-and-embeddings
---


---
layout: end
---
