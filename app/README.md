# RAG demo app

The live demo for the [RAG & Embeddings session](../notes/Session-Outline.md). Five
questions, a six-step wizard: four go green from retrieval tricks alone, the fifth
needs the last step, Structure.

## Run it

```bash
cd app
export UV_PROJECT_ENVIRONMENT="$HOME/.venvs/rag-demo"   # keeps torch out of Dropbox
uv sync
uv run python scripts/build_index.py
uv run uvicorn --factory web.server:build --port 8000
```

The environment lives outside the repository on purpose: this checkout sits in a Dropbox
folder, and a local `.venv` would sync several gigabytes of torch. Set the variable in
your shell profile and forget about it.

That runs against `sample/`, a synthetic corpus of eight invented consultants and two
invented policies. It reproduces every failure and every fix.

## Run it on real data

Drop the real corpus into `app/data/raw/`, which is gitignored in full:

```
data/raw/pdfs/*.pdf          policies — indexed as source_type "policy"
data/raw/cvs/*.pdf|*.docx    consultant CVs
data/raw/projects/*.pdf|*.md project sheets (optional)
data/raw/bamboo/*.json       BambooHR export, one array of records per file
```

`build_index.py` prefers `data/raw/` over `sample/` when it exists. Build the real
index to `data/index-real` explicitly — the server prefers it over `data/index` when
it exists, so nothing else needs to change to switch the demo to real data:

```bash
uv run python scripts/build_index.py --out data/index-real
```

Nothing under `data/` is ever committed: chunks are plaintext CV and HR text, embeddings
can be inverted back to approximate text, and cached answers quote both.

Compensation, performance reviews and leave reasons stay out of the export.

## Before the talk

```bash
uv run pytest -m slow                  # the 30-assertion scoreboard
uv run python scripts/warm_cache.py    # every question at every step
```

Both need a Claude credential:

```bash
ant auth login
```

That writes an OAuth profile to `~/.config/anthropic/`, which the SDK picks up with no
API key and no environment variable. The token lasts 8 hours and refreshes itself; log
in again if it has gone stale.

`warm_cache.py` warms `build_engine()`'s default index (`data/index`). The server
prefers `data/index-real` when it exists, so before the talk edit the script's
`build_engine()` call to pass `data/index-real` explicitly — otherwise the retrieved
chunks differ from what the cache was warmed against, and the live demo still hits the
network.

## Commands

| Command                                                 | Does                                    |
| ------------------------------------------------------- | --------------------------------------- |
| `uv run pytest`                                         | Unit tests, no models, no network       |
| `uv run pytest -m slow`                                 | The scoreboard, against the built index |
| `uv run python scripts/build_index.py`                  | Ingest, embed, project                  |
| `uv run python scripts/warm_cache.py`                   | Fill the answer cache                   |
| `uv run uvicorn --factory web.server:build --port 8000` | Serve the app                           |
