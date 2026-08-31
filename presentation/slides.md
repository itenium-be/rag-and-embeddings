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
layout: agenda
items:
  - RAG
  - Embeddings
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
h1:
  type: braces
  color: primary
  position: all
---

# RAG

## An Example

<WithoutRag :clicks="$clicks" />

---
layout: default
clicks: 6
h2:
  type: dot
  color: secondary
  position: end
---

# RAG

## Adding the answer to the prompt

<WithRag :clicks="$clicks" />


---
layout: default
clicks: 6
h2:
  type: dot
  color: secondary
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
h2:
  type: dot
  color: secondary
  position: end
---

# Embeddings

## Just paste them all in?

<ContextWindow :clicks="$clicks" />

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
