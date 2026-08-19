# Ingestion

Fills gap 6 in [Gaps](Gaps.md). The book notes cover chunking well — size, overlap,
contextual embedding — and stop there. Everything *before* the chunker, and everything about
running it a second time, is missing. This is where most real projects stall.

## Getting to the text

Chunking assumes you have text. For the CVs and project sheets in
[Demo Data](Demo-Data.md), you do not — you have PDFs and Word files with layout.

**Reading order is the first trap.** Consultant CVs are frequently two-column, and a naive
PDF text extractor reads straight across the page, interleaving the sidebar with the body.
The output looks like text, embeds without complaint, and is nonsense. Always eyeball the
extracted text of a few documents before trusting a corpus — this failure is silent and
survives all the way to a wrong answer.

**Tables are the classic killer.** A skills matrix or a rate card chunked by character count
gets sliced mid-row, and the header — which is what gives the numbers meaning — ends up in a
different chunk from the data. Extract tables separately, convert to markdown or HTML, and
keep each table whole even if it breaks your size budget. If a table is genuinely too large,
repeat the header row in each piece.

**Scans need OCR.** Anything that arrived as a photocopy has no text layer at all. Check for
this explicitly — a PDF with zero extractable characters should raise an error in your
pipeline, not quietly contribute nothing.

Tools worth naming: PyMuPDF and pdfplumber for the mechanical extraction, `unstructured` and
Docling for layout-aware parsing, and the cloud document-intelligence services (Azure, AWS
Textract) when the documents are messy enough to justify the cost.

## Running it twice

The first ingestion is easy. The second one is where the design shows.

**Chunk IDs must be deterministic.** Derive them from something stable —
`hash(document_id + chunk_index)` or `hash(document_id + chunk_text)` — so that re-running
ingestion *upserts* instead of duplicating. A pipeline that appends on every run silently
fills the index with near-duplicates, and retrieval starts returning the same chunk five
times, crowding out everything else.

**Content hashing saves the embedding bill.** Hash each chunk's text; if the hash is
unchanged, skip the embedding call. For a corpus where a handful of CVs change per week,
this turns a full re-embed into almost nothing.

**Deletes must be real.** When a consultant leaves or a document is withdrawn, the chunks
have to go. Two things to remember: you need a document→chunks mapping to find them, and
HNSW deletes are tombstones (see [Vector Indexes](Vector-Indexes.md)) — the graph does not
heal, so a heavily-churned index needs periodic rebuilding.

**Update = delete + insert, not edit.** A shortened document leaves orphaned chunks behind
if you only overwrite. Delete all chunks for the document, then re-insert.

## Changing the embedding model is a migration

The book notes mention this in a clause — "changes to the embedding model require all
documents to be re-setup". It deserves a plan, because you cannot mix vectors from two
models in one index and get meaningful distances.

The safe pattern is a **parallel build**: create the new index alongside the old, backfill
it, verify quality on your eval set, then swap a pointer. Never migrate in place — you have
no rollback, and quality regressions from an embedding change are not always obvious in the
first hour.

Keep the source text alongside the vectors so a re-embed never requires re-parsing the
original PDFs. Parsing is the slow, fragile step; do it once.

## Keep an ingestion manifest

Record per document: source, content hash, parser used, chunk count, embedding model and
version, and ingestion timestamp. It takes an afternoon and it answers the questions you
will actually be asked — *why is this document not being found*, *when did this last update*,
*which model embedded this*. Without it you are debugging a black box.

## For the session

This is part 9 of the [outline](Session-Outline.md), and it is the least glamorous material
in the session — which is exactly why it is worth including. Everyone demos chunk-embed-
retrieve; almost nobody mentions that the demo becomes a maintenance problem the moment it
has real users.

If you want one slide: the two-column CV. Show the extracted text, let the room read the
interleaved nonsense, and point out that nothing in the pipeline would ever have told you.
