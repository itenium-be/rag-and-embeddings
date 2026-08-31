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
layout: socials
---

---
layout: source
source: itenium-be/rag-and-embeddings
---


---
layout: end
---
