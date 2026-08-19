# Foundations — for a room that has not done this before

Written for an audience arriving without RAG, embeddings, vector search or GraphRAG. Nothing
here assumes prior exposure. This is the material the rest of the notes take for granted.

The trap when you know a subject well is starting one layer above where the room is. Every
section below exists because skipping it loses people quietly — they stop asking questions
and wait for the end.

## 1. What the model does not know

Start here, not with RAG. The problem has to be felt before the solution means anything.

An LLM learned from an enormous amount of text up to a cutoff date. That gives it language,
reasoning and broad world knowledge. It gives it **nothing** about:

- anything after the cutoff
- anything private — your BambooHR, your CVs, your project sheets
- anything that changed since

And the failure mode is the important part: **it answers anyway.** It does not know what it
does not know. Ask it who at itenium is AZ-204 certified and you will get a fluent,
well-structured, entirely invented answer.

> **Live opener.** Ask the model a question about your own company before showing any
> architecture. The invented answer is the whole motivation for the session, and it is more
> persuasive than any slide.

Two options for fixing this. **Training** the model on your data — expensive, slow, needs
redoing whenever anything changes, and it still will not reliably recall specific facts.
Or **showing it the relevant documents at question time**. The second is what the rest of
the session is about.

## 2. The open-book exam

That is the whole idea:

> A closed-book exam is the model answering from memory. RAG is an **open-book exam** — but
> the book is enormous, so someone has to find the right pages first and put them in front
> of the model along with the question.

**RAG = Retrieval-Augmented Generation.** Retrieval: find the relevant pages. Augmented:
staple them to the question. Generation: the model answers from what it can see.

Say the expansion once and then keep using the exam. One analogy, used consistently, beats
four clever ones.

Three things worth pre-empting, because someone is thinking them:

- **This is not training.** The model learns nothing. The documents ride along in the
  question and are gone afterwards.
- **It does not remember.** Every question starts fresh.
- **It can still be wrong.** Retrieval can fetch the wrong pages, and the model can misread
  the right ones. RAG improves the odds; it does not make the system truthful.

## 3. Finding the right pages

Everyone in the room already knows one way: **keyword search**. Type a word, get documents
containing it. Fast, exact, and it has an obvious limit — someone searching "who knows
container orchestration" finds nothing in a CV that says "5 years Kubernetes".

So we need to match on **meaning** rather than spelling. That is what embeddings do — and it
is worth pausing here, because this is the concept the session is named after and the one
people most often nod along to without getting.

## 4. Embeddings — a map of meaning

**Show a vector before defining one.** Put a real, truncated one on screen:

```
"5 years of Kubernetes and Docker"  →  [0.021, -0.184, 0.077, 0.310, ... ]  (1536 numbers)
```

Then the idea:

> An embedding model reads a piece of text and gives it **coordinates on a map of meaning**.
> Texts that mean similar things land near each other. Texts about different things land far
> apart. It does not matter whether they share any words.

The map has 1536 dimensions rather than 2, which nobody can picture — and does not need to.
The only property that matters is **near = similar**.

> **The demo that makes it land.** Take thirty sentences from the CVs, embed them, squash to
> 2D and plot. The infrastructure people cluster here, the frontend people there, the data
> people over there — and nobody wrote those groupings. Let the room look at it in silence
> for a moment. This is the single most valuable minute in the session; a beginner who *sees*
> the clustering understands embeddings, and one who only hears "vectors in high-dimensional
> space" does not.

Then the mechanical follow-up: a search means embedding the **question** with the same model
and returning the nearest documents. That is vector search, and it is genuinely all it is.

Two honesty notes, both cheap and both worth making:

- **The map is learned, not discovered.** It reflects the examples the model was trained on.
  A model trained on web text has a fine map of general English and a poor map of your
  internal jargon. This is why the session later talks about choosing models.
- **Two different models are involved.** One turns text into coordinates; a different one
  writes the answer. Beginners routinely merge these into a single "the AI", and every later
  discussion of cost, choice and re-embedding gets confusing until they are separated. Draw
  them as two boxes and keep them separate all session.

## 5. Why documents get chopped up

You cannot embed a 40-page document as one point on the map — its meaning is not one thing,
and you would retrieve the whole document to answer a question about one paragraph.

> Tear the book into **index cards**. Each card gets its own coordinates. Retrieval returns
> cards, not books.

That is chunking, and every awkward decision later — how big, where to cut, how much overlap
— follows from it. It is also the source of the failures in part 2 of the session: a card
torn out of a table loses its header, and a card about "the October handover" no longer says
which project it belonged to.

## 6. The whole pipeline, in six boxes

Draw this once and refer back to it all session. Every technique later is a modification to
one box.

```
INGESTION  (once, up front)
  documents → chop into chunks → embedding model → coordinates → store

QUERY  (every question)
  question → embedding model → coordinates → find nearest chunks
           → paste chunks + question into a prompt → answer model → answer
```

Six boxes. When hybrid search arrives, it changes "find nearest". When reranking arrives, it
adds a box. When the graph arrives, it replaces "find nearest" with "run a query". Anchoring
everything to one diagram is what keeps a beginner audience oriented.

## 7. Name the two families early

The room will hear "vector RAG" and "GraphRAG" repeatedly. Define them in one line each,
before they are needed, so the words are familiar rather than intimidating:

- **Vector RAG** — everything above. Chop documents into cards, find the cards nearest the
  question. Good at *"what does it say about X"*.
- **GraphRAG** — pull the facts out of the documents into a network of things and how they
  relate (this consultant → has skill → Kubernetes). Then answer by querying the network.
  Good at *"how many"*, *"which ones"*, and *"what is true across everything"*.

Then promise to come back to the second one, and move on. The five-question scoreboard will
do the actual explaining — the difference between the two families is much easier to see
once the room has watched vector RAG fail at counting.

## 8. Words to define the first time you use them

Beginners get lost less from difficult concepts than from vocabulary that arrives
undefined — and from the same idea having three names. See [Glossary](Glossary.md); handing
it out on paper at the start is worth more than it sounds.

The ones that trip people most:

| Say | Not | Because |
| --- | --- | --- |
| chunk | passage / segment / document / node | pick one word and never vary it |
| coordinates, or embedding | vector / representation / latent | "vector" is fine once, after the map |
| the answer model | the LLM / the model / GPT | there are two models; say which |
| store | vector database / index / VDB | "index" also means something else |

## 9. What to leave out

For a first session, actively **do not** cover: HNSW internals, quantization, ANN recall
tuning, `ef_search`, bi-encoder versus cross-encoder architecture, or the vector store
comparison. None of it helps someone who does not yet know what a chunk is, and all of it
signals "this is complicated", which is the opposite of what a first session should leave
behind.

Reranking still belongs — but as *"ask a slower, more careful model to re-sort the shortlist"*,
which is true and sufficient. The architecture behind it is
[session two material](Reranking.md).
