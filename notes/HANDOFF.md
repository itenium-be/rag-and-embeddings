# Handoff prompt — RAG & Embeddings deck

Paste everything below the line into a fresh session.

---

We're building a Slidev deck for an itenium session on RAG & Embeddings
(2h target, 60min minimum, presented 2026-09-01 — TODAY).

**THIS SESSION'S JOB: slide 15 — `Retrieval / Every question`.** It is built but has not
been reviewed on screen. Read "SLIDE 15" at the bottom first, then propose before
changing anything.

REPO: /mnt/c/Users/woute/Dropbox/Personal/Programming/UnixCode/courses/2026-09-01-RAG-Embeddings
Deck in `presentation/`. Notes in `notes/` (read `notes/Session-Outline.md`).
The demo webapp in `app/` is essentially DONE and is built by a SEPARATE Claude session.
Never commit `app/`, `midjourney.md`, `.gitignore`, or `docs/superpowers/`.

=== HOW WOUTER WORKS — READ THIS FIRST ===
1. He edits files by hand between turns. NEVER overwrite his changes.
   - Never `cat >` or Write over an existing file. Use Edit/python with exact anchors.
   - Before any full-file rewrite, run `git status --short <file>` — clean against HEAD
     means the rewrite is recoverable; otherwise targeted edits only.
   - Commit each change as soon as it renders, so git is the fallback.
   - **Anchor on the `## Title` line, never on frontmatter.** Two slides share
     `clicks: 2`; a regex anchored on frontmatter inserted a slide in the wrong place
     this session. It was recoverable only because `git diff --stat` showed 0 deletions.
2. Never change his wording, capitalization, or `<br>` tags. Layout/CSS only, unless he
   asks for copy.
3. Never screenshot to verify your own work — assert with measurement.
   **The MCP browser is usually locked by another session.** Use headless instead:
   ```js
   import { chromium } from '<repo>/presentation/node_modules/playwright-core/index.mjs'
   ```
   Slidev scales the slide: multiply by `(980 / slideRect.width)` for design px.
   The slide is 980x613 design px; the text column is x=96..940. 1rem = 16 design px.
   Slidev keeps neighbouring slides in the DOM at zero size — pick the active one with
   `[...document.querySelectorAll('.slidev-layout')].find(e => e.getBoundingClientRect().width > 100)`.
   `scrollHeight` does NOT detect overflow in a centred flex box; union the child rects.
4. One slide at a time. Propose, get agreement, build, verify, move on.
5. Terse. Show changed code, not whole files. No preamble.
6. When something is genuinely visual (optical centring, "does this look balanced"),
   say so and give him the URL — do not claim you verified it.

=== DEV SERVER ===
`cd presentation && bunx slidev --port 3031`  (bun/bunx, never npm/npx)
Likely ALREADY RUNNING. Then: `http://localhost:3031/<slide>?clicks=<n>`

GOTCHAS THAT COST HOURS:
- /mnt/c under WSL emits no inotify events. `vite.config.ts` sets usePolling — after
  editing, `sleep 7` before measuring or you measure a stale module.
- Don't reinstall inside `presentation/theme/` (duplicate Vue → app won't mount).
- Blank lines inside an HTML block in slides.md silently break the deck.
  `<style>` in a slide must NOT be scoped.
- Multi-root Vue components: only the first root renders. Always one root.
- `$clicks` (not `clicks`) is the template variable: `<Comp :clicks="$clicks" />` plus
  `clicks: N` in frontmatter. **After reworking reveals, re-check the frontmatter count.**
- Grid columns: a third of the width is NOT a column centre once `gap` is subtracted.
  Derive centres with `calc((100% - 2 * var(--gap)) / 6)` — this bit twice.
- Adjacent vertical margins collapse; `margin-top` on a sibling may buy you nothing.
- Layouts/components documented in `presentation/theme/LAYOUTS.md` — read it.
- `TitleDecoration.vue` only knows colors `primary` and `muted`. `secondary` silently
  falls back to primary.

=== HOUSE STYLE ===
- He says "it's very light / muted" a LOT. NEVER dim unrevealed content with partial
  opacity. Reveal = opacity 0 -> 1, keeping the space so nothing reflows.
  Body text #33343a or darker, borders #a8a8a8 not #d8d8d8.
- Palette: charcoal #343434, orange var(--color-primary) #e84700, green #3f8a46 /
  #276b2e / #edf6ee, problem-red #b23c2c, highlight #ffe2d2 on #8a2f00, muted #5f6066.
- Fill the slide: 85-90% vertical fill. Measure it; he objects to content in the top half.
- Arrows are the ← / → glyphs. A drawn connector uses an open chevron (rotated
  border-right+border-bottom), never a filled triangle. Connectors leave an **8px gap**
  before the box they point into — that is the deck's existing arrow clearance.
- Align by shared column widths / CSS vars, then assert offset === 0 with evaluate.
- No invented data. Every number and sample is pulled from `app/data/index-real`.

=== DECK AS BUILT (22 slides) ===
```
 1 cover                                          12 Embeddings / A map of meaning      MeaningMap    (3)
 2 agenda                                         13 Embeddings / Comparing two vectors DotProduct    (7)
 3 section "RAG"                                  14 Embeddings / The whole pipeline     Pipeline      (9)
 4 RAG / RAG What?           RagBox      (3)      15 Retrieval  / Every question         QueryPipeline (5)  <-- TODAY
 5 RAG / An Example          WithoutRag  (6)      16 Embeddings / Five questions         Scoreboard    (2)
 6 RAG / Adding the answer   WithRag     (6)      17 break
 7 Use Case / Consultants... UseCase     (2)      18 Making it work / Hybrid search      HybridSearch  (4)
 8 section "Embeddings"                           19 What we left out (his table)
 9 Embeddings / Just paste them all in? ContextWindow (5)    20 socials
10 Chunking  / Split into pieces        Chunking      (5)    21 source
11 Embedding / Chunks to vectors        RealVector    (3)    22 end
```
Shared glyphs: `StochasticParrot.vue`, `ProgrammerGlyph.vue`.

Title decorations are deliberately on only ~40% of content slides: 4 braces/primary,
7 dot/primary, 10 hash/muted, 13 slashes/muted, 18 semicolon/muted. Leave the rest bare.

=== KEY FACTS, MEASURED — DO NOT RE-DERIVE OR CONTRADICT ===
- Model: `intfloat/multilingual-e5-small` => **384 dims**, NOT 1536. `hidden_size 384`,
  12 heads x 32, 12 layers, BERT, 512 max positions. `notes/Foundations.md` still says
  1536 and is WRONG for this deck.
- Corpus: 2194 chunks, 63 documents, ~220k tokens. 40 CVs, 20 policy PDFs, a credits
  ledger.
- Chunking: `split_text(size=800, overlap=100)`, recursive on `¶ → line → sentence → word`.
  Arbeidsreglement.pdf = 37 pages, 92,190 chars, 133 chunks.
- All vectors are normalised to length 1.0000, so **dot product IS cosine**.
- All 2,405,721 chunk pairs: min **0.661**, p1 0.730, median 0.800, mean 0.812,
  p99 0.929, max 0.999 (two BambooHR rows for one person differing by a date).
- Question 1 "Welke AI tools mag ik gebruiken?" vs its top chunk = **0.887**.
- AZ-900 question: 5 CVs hold it. Dense top-5 finds 1, BM25 finds 3, RRF finds 4.
- Store = `chunks.jsonl` (1.3 MB) + `embeddings.npy` (3.2 MB, 2194 x 384 float32).
  No database. Search is `vectors @ query_vector` then argsort.
- Answer model: `claude-opus-5` via the `claude` CLI.
- **Real query path** (`app/rag/pipeline.py` `Engine.run`):
  `question → (rewrite_query if config.rewrite) → retrieve(dense + bm25, RRF-fused)
   → (apply_rerank if config.rerank) → top_n → generate_answer(question, used) → citations`
  `embed_query` prefixes `"query: "` (chunks got `"passage: "`); it touches no store.
  The store is used one step later, inside `DenseIndex.search`.
- `app/rag/models.py` WIZARD_STEPS: 1 Naive, 2 Hybrid, 3 Reranking, 4 Query rewriting,
  5 Citations, 6 Structure. `app/questions.yaml` five questions MATCH the deck's five.

=== WHAT'S NEXT (after slide 15) ===
Slide 16 hands off to the APP. Everything from there alternates deck <-> app:
  -> app: the 2D cluster plot (`data/index/projection.npy`, `umap.UMAP(n_components=2,
     metric="cosine")`) — the most valuable minute of the session. Sits between slides
     12 and 13 in delivery even though it isn't a slide.
  -> app: wizard step 1 (Naive) against the five questions
  then each as a deck slide in front of its app step: Hybrid search (18, BUILT) ·
  Reranking · Query rewriting · Citations · "vectors cannot count".
  Close on `notes/When-Not-To-RAG.md`.
Keyword search deliberately does NOT get its own slide before hybrid search. DECIDED.

=== SLIDE 15 — WHAT YOU ARE WORKING ON ===
`presentation/components/QueryPipeline.vue`, `clicks: 5`, currently:

```
        "Wie kan me helpen met Kubernetes?"          (orange query bar)
                        |
              [ retriever agent ]                    decides where to look
          /             |             \
  [vector search]  [API call]     [SQL query]
  nearest chunks   BambooHR, live  count, sum, join
  THIS DEMO        NOT TODAY       NOT TODAY
          \             |             /
              [ stuffed into the prompt ]            the model only ever sees
                        |                            what retrieval handed it
              [ answer model ] -> [ answer + citations ]
```
Clicks: 1 query bar · 2 agent · 3 fan + three sources · 4 converge + prompt · 5 tail.
Verified: connector legs land on source-box centres at 0.0px drift; 88.5% fill.
Connectors are `.rule` (2px) + `.chev` (open chevron) primitives.

**Known problems, all his to decide:**
1. **It contradicts slide 19.** The "What we left out" table says *"Router, agents,
   critic — Let a model pick the retriever, then check its own answer — Session 2"*,
   while this slide draws exactly that. He accepted the contradiction knowingly. The row
   may want rewording to something like "we drew the router; running it is session 2".
2. **The app does neither the API call nor the SQL query** — vector + BM25 only. They
   are marked `NOT TODAY`; keep that honest, do not imply they run.
3. **The question may be the wrong one.** It uses the Kubernetes question. Question 5,
   `"Hoeveel credits heeft Simon nog?"`, would motivate the SQL route far better — no
   chunk contains the answer, it has to be counted. Risk: it pre-empts the finale, which
   the outline says to foreshadow but not explain.
4. **Slide 14 was just re-decomposed and this slide should probably follow.** Its query
   row is now `question → embedding model → search → nearest chunks + question →
   answer model`, i.e. the *search operation* is its own box, separate from the *result*.
   Slide 15 still collapses those into one hop.
5. Slide 14 also lost its "Two different models" line and now sits at **72% fill**;
   fixing that needs `.phase.second` padding AND the `.elbow` height moved together,
   since the elbow is calibrated to the inter-row gap.

Ask about anything ambiguous rather than guessing. Start by reading
`presentation/slides.md`, `theme/LAYOUTS.md` and `components/QueryPipeline.vue`.
