RAG and Embeddings
==================

Material for the itenium session on **RAG & Embeddings**: vector RAG from the ground up,
built around five questions of which the naive pipeline answers one.

- [Elevator pitch](ElevatorPitch.md) — abstract, audience, takeaways
- [Notes](notes/README.md) — session outlines and the background material
- [Demo app](app/README.md) — the live demo

## Presentation

```bash
cd presentation
bun install
bun run dev
```

Update the theme:
```bash
cd presentation/theme
git pull
```

## Demo app

```bash
cd app
export UV_PROJECT_ENVIRONMENT="$HOME/.venvs/rag-demo"
uv sync
uv run python scripts/build_index.py
uv run uvicorn --factory web.server:build --port 8000
```

Runs against the synthetic corpus in `app/sample/`. See [app/README.md](app/README.md)
for real data, the wizard steps and the tests.
