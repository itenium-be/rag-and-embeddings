# RAG Demo App Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the live demo for the RAG & Embeddings session — a five-step wizard over one corpus that flips four of five questions from red to green while the fifth stays permanently red.

**Architecture:** A `rag/` package holding the pipeline (parse → chunk → embed → retrieve → rerank → generate), driven by one frozen `Config` whose presets are the wizard steps. Embeddings and reranking run locally via sentence-transformers; only query rewriting and answer generation call Claude, and both are disk-cached. A FastAPI server hands a single static HTML page a JSON API.

**Tech Stack:** Python 3.12 with uv, pytest, sentence-transformers (`bge-small-en-v1.5`, `bge-reranker-base`), rank-bm25, umap-learn, numpy, pypdf, python-docx, FastAPI, Alpine.js and Plotly from CDN, `anthropic` SDK authenticated via the `ant auth login` OAuth profile.

**Spec:** [2026-08-31-rag-demo-app-design.md](../specs/2026-08-31-rag-demo-app-design.md)

---

## Running commands

**Every `uv` command in this plan needs these two exported first:**

```bash
export PATH="$HOME/.local/bin:$PATH"
export UV_PROJECT_ENVIRONMENT="$HOME/.venvs/rag-demo"
```

The repository lives inside a Dropbox folder on a `/mnt/c` drvfs mount. A default
`app/.venv` would put several gigabytes of torch into Dropbox's sync set — `.gitignore`
stops git seeing it and does nothing about Dropbox — and thousands of small files on
drvfs are slow to write and slower to import. The environment therefore lives outside the
synced tree. Nothing else about the project changes.

## Deviations from the spec

Three, all deliberate:

1. **`rag/models.py` instead of `rag/chunks.py`.** The spec put the dataclasses in `chunks.py`, but `Config` has to be importable by both `retrieve.py` and `pipeline.py` without a cycle. One module of pure data types, no logic, no imports from the rest of the package.
2. **The virtualenv lives at `~/.venvs/rag-demo`, not `app/.venv`.** See *Running
   commands* above.
3. **8 sample consultants, not ~15.** Eight is enough for all five questions to behave: one AZ-204 holder plus two AZ-decoys, one deep Kubernetes expert plus four shallow mentions, one ACME assignment ending in September. Fifteen would be seven more CVs to hand-write with no extra demonstrative power.

## File structure

| File | Responsibility |
| --- | --- |
| `app/pyproject.toml` | Deps, pytest config, package discovery |
| `app/.gitignore` | Excludes `data/` in full |
| `app/rag/models.py` | `Chunk`, `Scored`, `Citation`, `Config`, `Result`, `WIZARD_STEPS` — pure data |
| `app/rag/chunking.py` | Text splitting, deterministic chunk ids |
| `app/rag/ingest.py` | Per-source-type parsing and chunking → `chunks.jsonl` |
| `app/rag/embed.py` | sentence-transformers wrapper, L2-normalised vectors |
| `app/rag/index.py` | `DenseIndex` (numpy cosine), `Bm25Index` (rank-bm25 + a tokenizer that keeps `az-204` and `xximo` whole) |
| `app/rag/fuse.py` | Reciprocal rank fusion |
| `app/rag/rerank.py` | `Reranker` protocol, cross-encoder implementation |
| `app/rag/llm.py` | `LLM` protocol, Anthropic implementation, disk cache wrapper |
| `app/rag/rewrite.py` | Step-back query rewriting |
| `app/rag/generate.py` | Answer generation with citations |
| `app/rag/pipeline.py` | `Engine` — holds indexes and models, runs a `Config` |
| `app/web/server.py` | FastAPI routes |
| `app/web/static/index.html` | The whole UI |
| `app/scripts/build_index.py` | ingest + embed + project |
| `app/scripts/warm_cache.py` | Every question × every wizard step |
| `app/sample/` | Committed synthetic corpus |
| `app/questions.yaml` | The five questions and their expected verdict per step (6 steps) |

---

### Task 1: Project scaffold

**Files:**
- Create: `app/pyproject.toml`
- Create: `app/.gitignore`
- Create: `app/rag/__init__.py`
- Create: `app/tests/__init__.py`
- Create: `app/tests/test_scaffold.py`

- [ ] **Step 1: Create the project directory and pyproject**

```bash
mkdir -p app/rag app/tests app/web/static app/scripts app/sample
```

`app/pyproject.toml`:

```toml
[project]
name = "rag-demo"
version = "0.1.0"
description = "Live demo for the itenium RAG & Embeddings session"
requires-python = ">=3.12"
dependencies = []

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["rag", "web"]

[tool.pytest.ini_options]
testpaths = ["tests"]
markers = [
    "slow: needs the real embedding models on disk (deselect with '-m \"not slow\"')",
]
addopts = "-m 'not slow'"
```

- [ ] **Step 2: Create the gitignore**

`app/.gitignore`:

```
data/
.venv/
__pycache__/
.pytest_cache/
```

- [ ] **Step 3: Create empty package markers**

```bash
touch app/rag/__init__.py app/tests/__init__.py
```

- [ ] **Step 4: Write a scaffold test**

`app/tests/test_scaffold.py`:

```python
import rag


def test_package_imports():
    assert rag is not None
```

- [ ] **Step 5: Add dependencies and run the test**

```bash
cd app
uv add anthropic fastapi "uvicorn[standard]" numpy pypdf python-docx pyyaml rank-bm25 sentence-transformers umap-learn
uv add --dev pytest httpx
uv run pytest -v
```

Expected: `test_package_imports PASSED`. The `uv add` calls write resolved versions into `pyproject.toml` and create `uv.lock`.

- [ ] **Step 6: Commit**

```bash
git add app/pyproject.toml app/uv.lock app/.gitignore app/rag/__init__.py app/tests/__init__.py app/tests/test_scaffold.py
git commit -m "Scaffold the RAG demo app"
```

---

### Task 2: Data models

**Files:**
- Create: `app/rag/models.py`
- Test: `app/tests/test_models.py`

- [ ] **Step 1: Write the failing tests**

`app/tests/test_models.py`:

```python
from rag.models import WIZARD_STEPS, Config


def test_wizard_has_six_steps_and_accumulates():
    assert len(WIZARD_STEPS) == 6
    assert WIZARD_STEPS[0].config == Config()
    assert WIZARD_STEPS[1].config.bm25
    assert WIZARD_STEPS[2].config.bm25 and WIZARD_STEPS[2].config.rerank
    assert WIZARD_STEPS[3].config.rewrite
    assert WIZARD_STEPS[4].config.citations
    assert WIZARD_STEPS[5].config.aggregates


def test_aggregates_are_off_until_the_last_step():
    assert not Config().aggregates
    assert all(not s.config.aggregates for s in WIZARD_STEPS[:5])
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `cd app && uv run pytest tests/test_models.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'rag.models'`

- [ ] **Step 3: Write the implementation**

`app/rag/models.py`:

```python
"""Pure data types. Imports nothing else from `rag`, so every module can use them."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Chunk:
    id: str
    text: str
    source: str
    source_type: str  # policy | cv | project | assignment | credit | aggregate
    title: str
    location: str
    metadata: dict = field(default_factory=dict)


@dataclass(frozen=True)
class Scored:
    chunk: Chunk
    score: float
    # Rank at each stage the chunk passed through, 1-based: {"dense": 12, "rerank": 1}.
    # This is what makes a technique's effect visible on the projector.
    ranks: dict[str, int] = field(default_factory=dict)


@dataclass(frozen=True)
class Citation:
    marker: int
    chunk_id: str
    title: str
    location: str


@dataclass(frozen=True)
class Config:
    dense: bool = True
    bm25: bool = False
    rerank: bool = False
    rewrite: bool = False
    citations: bool = False
    # Lets precomputed summary chunks into retrieval. Off for the first five steps so
    # the room sees the ledger fail before it sees structure fix it.
    aggregates: bool = False
    top_k: int = 50  # retrieve wide
    top_n: int = 5   # keep few


@dataclass(frozen=True)
class Result:
    question: str
    rewritten: str | None
    candidates: list[Scored]
    used: list[Scored]
    answer: str
    citations: list[Citation]


@dataclass(frozen=True)
class WizardStep:
    number: int
    name: str
    blurb: str
    config: Config


WIZARD_STEPS: list[WizardStep] = [
    WizardStep(
        1,
        "Naive",
        "Embed the question, return the nearest chunks.",
        Config(),
    ),
    WizardStep(
        2,
        "Hybrid search",
        "Run keyword search alongside meaning search and merge the two.",
        Config(bm25=True),
    ),
    WizardStep(
        3,
        "Reranking",
        "Fetch 50 candidates, let a slower model re-sort them, keep 5.",
        Config(bm25=True, rerank=True),
    ),
    WizardStep(
        4,
        "Query rewriting",
        "Broaden the question before searching for it.",
        Config(bm25=True, rerank=True, rewrite=True),
    ),
    WizardStep(
        5,
        "Citations",
        "Track which chunk every claim came from.",
        Config(bm25=True, rerank=True, rewrite=True, citations=True),
    ),
    WizardStep(
        6,
        "Structure",
        "Compute the answer at ingest time instead of retrieving it. "
        "This is not a retrieval technique — it is the next session.",
        Config(bm25=True, rerank=True, rewrite=True, citations=True, aggregates=True),
    ),
]
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `cd app && uv run pytest tests/test_models.py -v`
Expected: 2 passed

- [ ] **Step 5: Commit**

```bash
git add app/rag/models.py app/tests/test_models.py
git commit -m "Add RAG data models and wizard step presets"
```

---

### Task 3: Chunking

**Files:**
- Create: `app/rag/chunking.py`
- Test: `app/tests/test_chunking.py`

- [ ] **Step 1: Write the failing tests**

`app/tests/test_chunking.py`:

```python
from rag.chunking import chunk_id, split_text


def test_short_text_is_one_chunk():
    assert split_text("hello world", size=800, overlap=100) == ["hello world"]


def test_long_text_splits_on_paragraph_boundaries():
    text = "\n\n".join(f"Paragraph {i}. " + "word " * 40 for i in range(6))
    parts = split_text(text, size=400, overlap=50)
    assert len(parts) > 1
    # A chunk carries its predecessor's tail, so the ceiling is size + overlap.
    assert all(len(p) <= 400 + 50 + 1 for p in parts)


def test_consecutive_chunks_overlap():
    text = " ".join(f"w{i}" for i in range(400))
    parts = split_text(text, size=300, overlap=60)
    assert len(parts) > 1
    tail = parts[0][-40:]
    assert tail in parts[1]


def test_no_content_is_dropped():
    text = " ".join(f"w{i}" for i in range(400))
    parts = split_text(text, size=300, overlap=60)
    joined = " ".join(parts)
    for i in range(400):
        assert f"w{i}" in joined


def test_chunk_id_is_deterministic():
    assert chunk_id("cv/ana.md", 3, "text") == chunk_id("cv/ana.md", 3, "text")


def test_chunk_id_varies_with_every_input():
    base = chunk_id("cv/ana.md", 3, "text")
    assert chunk_id("cv/bram.md", 3, "text") != base
    assert chunk_id("cv/ana.md", 4, "text") != base
    assert chunk_id("cv/ana.md", 3, "other") != base
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `cd app && uv run pytest tests/test_chunking.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'rag.chunking'`

- [ ] **Step 3: Write the implementation**

`app/rag/chunking.py`:

```python
"""Recursive character splitting — the index-card metaphor from the session outline."""

from __future__ import annotations

import hashlib

SEPARATORS = ["\n\n", "\n", ". ", " "]


def chunk_id(source: str, ordinal: int, text: str) -> str:
    # Content is part of the id so a re-ingest after an edit produces a new id
    # rather than silently reusing a stale embedding.
    raw = f"{source}\x00{ordinal}\x00{text}".encode()
    return hashlib.sha256(raw).hexdigest()[:16]


def _split_on(text: str, separator: str, size: int) -> list[str]:
    pieces = text.split(separator)
    out: list[str] = []
    current = ""
    for piece in pieces:
        candidate = piece if not current else current + separator + piece
        if len(candidate) <= size:
            current = candidate
        else:
            if current:
                out.append(current)
            current = piece
    if current:
        out.append(current)
    return out


def split_text(text: str, *, size: int = 800, overlap: int = 100) -> list[str]:
    text = text.strip()
    if not text:
        return []
    if len(text) <= size:
        return [text]

    parts = [text]
    for separator in SEPARATORS:
        if all(len(p) <= size for p in parts):
            break
        expanded: list[str] = []
        for part in parts:
            expanded.extend(_split_on(part, separator, size) if len(part) > size else [part])
        parts = expanded

    # Anything still oversized has no separator left to break on.
    hard: list[str] = []
    for part in parts:
        while len(part) > size:
            hard.append(part[:size])
            part = part[size:]
        if part:
            hard.append(part)

    if overlap <= 0 or len(hard) == 1:
        return [p.strip() for p in hard if p.strip()]

    with_overlap = [hard[0]]
    for previous, part in zip(hard, hard[1:]):
        with_overlap.append(previous[-overlap:] + " " + part)
    return [p.strip() for p in with_overlap if p.strip()]
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `cd app && uv run pytest tests/test_chunking.py -v`
Expected: 6 passed

- [ ] **Step 5: Commit**

```bash
git add app/rag/chunking.py app/tests/test_chunking.py
git commit -m "Add recursive text splitting with deterministic chunk ids"
```

---

### Task 4: The sample corpus

No tests in this task — it is content, and everything downstream tests against it. It
mirrors the shape of `data/raw/` exactly (`pdfs/`, `cvs/`, `bamboo/*.csv`) so the ingest
code is exercised identically by the sample and the real thing.

Design constraints, one per question:

| Question | What the corpus must contain |
| --- | --- |
| 1 — opleidingsbudget | A policy section stating the amount plainly, easy to find by meaning |
| 2 — XXimo | A jargon term the embedding model has never seen, plus a semantically closer decoy document that dense retrieval grabs instead |
| 3 — Kubernetes | One deep expert whose CV chunk is diluted by other content, plus four shallow mentions in short chunks that score high on cosine |
| 4 — Lissabon | No chunk mentions Lisbon; a travel-expenses decoy does; the answer lives in a budget-scope section that only a broadened query reaches |
| 5 — credits | A ledger of signed per-event rows. The balance is in no chunk — it has to be summed |

**Files:**
- Create: `app/sample/pdfs/opleidingsbeleid.md`
- Create: `app/sample/pdfs/kilometervergoeding.md`
- Create: `app/sample/pdfs/xximo-kilometerstand.md`
- Create: `app/sample/pdfs/onkosten-en-reizen.md`
- Create: `app/sample/cvs/{ana-meeus,bram-claes,caro-dhondt,dries-peeters,elke-vermeulen,frank-nolens,gita-raman,hugo-willems}.md`
- Create: `app/sample/bamboo/consultants.csv`
- Create: `app/sample/bamboo/credits.csv`

- [ ] **Step 1: Write the policy documents**

`app/sample/pdfs/opleidingsbeleid.md`:

```markdown
# Opleidingsbeleid itenium

## Opleidingsbudget

Elke consultant beschikt over een jaarlijks opleidingsbudget van EUR 2000. Het budget
wordt toegekend op 1 januari en wordt niet overgedragen naar het volgende jaar.

Aanvragen onder EUR 500 worden goedgekeurd door je teamlead. Boven dat bedrag is ook
de goedkeuring van de practice manager nodig.

## Waarvoor mag het budget gebruikt worden

Het opleidingsbudget dekt cursusgeld, examengeld, vakliteratuur, en deelname aan
congressen en vakbeurzen, in binnen- en buitenland. Verplaatsing en verblijf bij een
meerdaags evenement vallen eveneens onder het budget.

Niet gedekt: hardware, software-licenties voor persoonlijk gebruik, en lidmaatschappen
van beroepsverenigingen.

## Certificaten

Examengeld wordt volledig terugbetaald bij een eerste geslaagde poging. Een herkansing
wordt eenmaal terugbetaald. Studiemateriaal telt mee voor het opleidingsbudget, het
examengeld zelf niet.

## Interne kennisdeling

Sessies die intern gegeven worden zijn betaalde tijd. Voorbereidingstijd tot tweemaal
de duur van de sessie is eveneens betaalde tijd.
```

`app/sample/pdfs/kilometervergoeding.md`:

```markdown
# Kilometervergoeding

## Vergoeding voor woon-werkverkeer

Wie met de eigen wagen naar een klant rijdt, ontvangt een kilometervergoeding volgens
het tarief dat de overheid jaarlijks publiceert. De vergoeding dekt brandstof, slijtage
en verzekering.

## Welke kilometers tellen mee

Kilometers tussen de woonplaats en de standplaats van de klant tellen mee. Kilometers
tussen kantoor en klant tellen mee. Privékilometers tellen niet mee.

## Wanneer indienen

De kilometerstand en de gereden kilometers worden maandelijks ingediend, samen met de
timesheet. Laattijdige indiening wordt verwerkt in de maand erna.

## Bedrijfswagen

Wie over een bedrijfswagen beschikt, heeft geen recht op kilometervergoeding voor
dezelfde verplaatsingen. De tankkaart of laadpas dekt die kosten.
```

`app/sample/pdfs/xximo-kilometerstand.md`:

```markdown
# XXimo kilometerstand ingeven

## Procedure

Log in op het XXimo portaal met je werkmailadres. Ga naar Mijn Wagen en kies
Kilometerstand doorgeven. Vul de stand in zoals die op de teller staat, zonder
decimalen, en bevestig.

## Frequentie

XXimo vraagt de stand elk kwartaal op. Je krijgt een herinnering per mail. Wie drie
opeenvolgende kwartalen niet doorgeeft, verliest tijdelijk toegang tot de laadpas.

## Foutieve stand

Een verkeerd ingegeven stand kan niet zelf gecorrigeerd worden. Mail dan naar de
fleetverantwoordelijke met de juiste stand en de datum van aflezing.
```

> The whole point of question 2. `kilometervergoeding.md` is semantically the closest
> thing to "hoe geef ik mijn kilometerstand door" and dense retrieval goes straight to
> it. `XXimo` is a brand the embedding model has never seen, so meaning-search is blind
> to it and BM25 is perfect at it.

`app/sample/pdfs/onkosten-en-reizen.md`:

```markdown
# Onkosten en buitenlandse reizen

## Verplaatsingen naar het buitenland

Reizen naar het buitenland voor een klantopdracht worden vooraf goedgekeurd door de
practice manager. Vluchten worden geboekt via het reisbureau, niet zelf.

## Dagvergoeding

Voor een verblijf in het buitenland geldt een forfaitaire dagvergoeding volgens de
landenlijst van de FOD Buitenlandse Zaken. Voor Portugal, Spanje en Italië geldt het
tarief voor Zuid-Europa.

## Voorbeelden

Een tweedaagse klantworkshop in Lissabon: vlucht en hotel via het reisbureau,
dagvergoeding volgens de landenlijst, maaltijden inbegrepen in de dagvergoeding.

## Bewijsstukken

Alle onkosten worden ingediend met een leesbaar bewijsstuk binnen de maand na de uitgave.
```

> The Lisbon decoy. Question 4 asked literally lands here — a document about travel
> expenses that genuinely mentions Lissabon — and never reaches the budget-scope section
> that actually answers it. Broadening the query to "waarvoor mag het opleidingsbudget
> gebruikt worden" is what fixes it.

- [ ] **Step 2: Write the eight CVs**

`app/sample/cvs/ana-meeus.md`:

```markdown
# Ana Meeus — Cloud Consultant

## Certifications

AZ-104 Microsoft Azure Administrator Associate. AZ-400 Designing and Implementing
Microsoft DevOps Solutions. Terraform Associate.

## Experience

Six years building and running Azure landing zones for mid-size enterprises. Designed
the subscription and policy structure for a retail group's migration of 200 workloads.
Comfortable across networking, identity and cost governance.

Runs the internal Azure guild and reviews landing zone designs across the company.
```

`app/sample/cvs/bram-claes.md`:

```markdown
# Bram Claes — Azure Developer

## Certifications

AZ-204 Developing Solutions for Microsoft Azure. Azure Fundamentals AZ-900.

## Experience

Five years of .NET on Azure. Builds serverless integrations with Azure Functions,
Service Bus and Event Grid. Took a logistics client's batch integration estate to an
event-driven design over eighteen months.

Strong on Cosmos DB modelling and on the messaging patterns that go with it. Deployed
those services to Kubernetes at a previous client.
```

`app/sample/cvs/caro-dhondt.md`:

```markdown
# Caro Dhondt — Data Consultant

## Certifications

AZ-104 Microsoft Azure Administrator Associate. DP-203 Data Engineering on Microsoft
Azure.

## Experience

Seven years in data platforms. Builds lakehouse architectures on Azure Databricks and
Synapse. Led the data platform rebuild for a Belgian insurer, including the migration
of forty legacy SSIS packages.

Teaches the internal Spark fundamentals course.
```

`app/sample/cvs/dries-peeters.md`:

```markdown
# Dries Peeters — Platform Engineer

## Certifications

CKA Certified Kubernetes Administrator. CKS Certified Kubernetes Security Specialist.
CKAD Certified Kubernetes Application Developer.

## Experience

Nine years in infrastructure, the last six of them on container platforms. Designed and
operates the internal developer platform that eleven teams deploy onto. Migrated forty
microservices from virtual machines onto a self-managed cluster, including the network
policy and admission control design that came with it.

Wrote the internal operator that manages tenant namespaces, quotas and secrets. Handles
cluster upgrades across three environments with no scheduled downtime. Regular reviewer
on infrastructure designs across the company, and the person other teams call when a
control plane misbehaves.

Also works on service mesh rollouts, observability with Prometheus and Grafana, and
supply chain security with Sigstore and Kyverno.
```

`app/sample/cvs/elke-vermeulen.md`:

```markdown
# Elke Vermeulen — Frontend Consultant

## Experience

Angular and React. Deployed to Kubernetes.
```

`app/sample/cvs/frank-nolens.md`:

```markdown
# Frank Nolens — Backend Consultant

## Certifications

AZ-900 Azure Fundamentals.

## Experience

Eight years of .NET. Currently on an integration platform, building event-driven flows
with Azure Service Bus, Azure Functions and NServiceBus. Cosmos DB read models and
Bicep for infrastructure.

Before that, four years on a payments platform. Deployed to Kubernetes.
```

`app/sample/cvs/gita-raman.md`:

```markdown
# Gita Raman — Data Engineer

## Experience

Python, Airflow, dbt. Deployed to Kubernetes.
```

`app/sample/cvs/hugo-willems.md`:

```markdown
# Hugo Willems — DevOps Consultant

## Experience

CI/CD with Azure DevOps and GitHub Actions. Kubernetes. Deployed to Kubernetes.
```

> The short CVs are short on purpose. A chunk that is almost entirely the word
> "Kubernetes" scores higher on cosine similarity than Dries' long chunk where the same
> word competes with nine years of other content. That is the failure question 3 needs,
> and reranking is what undoes it.

- [ ] **Step 3: Write the BambooHR exports**

`app/sample/bamboo/consultants.csv` — same header as the real export, including the
columns ingestion drops:

```csv
"Last name, First name",Status,"First Name","Middle Name","Birth Date",Gender,City,State,"Zip Code",Country,"Work Email","LinkedIn URL",Degree,College/Institution,Major/Specialization,"Hire Date",Startdatum,Einddatum,Functie,Klant
"Meeus, Ana",Active,Ana,,1990-04-11,Female,Antwerpen,Antwerpen,2000,Belgium,ana.meeus@example.be,,Master,KU Leuven,Informatica,2020-03-02,2024-01-08,2027-03-31,"Cloud Consultant",RetailCo
"Claes, Bram",Active,Bram,,1993-08-02,Male,Mechelen,Antwerpen,2800,Belgium,bram.claes@example.be,,Bachelor,AP Hogeschool,Toegepaste Informatica,2021-09-01,2025-02-03,2027-06-30,"Azure Developer",LogiTrans
"Dhondt, Caro",Active,Caro,,1988-12-19,Female,Gent,Oost-Vlaanderen,9000,Belgium,caro.dhondt@example.be,,Master,UGent,Wiskunde,2019-01-07,2024-09-02,2027-01-31,"Data Consultant",Insura
"Peeters, Dries",Active,Dries,,1986-06-30,Male,Leuven,Vlaams-Brabant,3000,Belgium,dries.peeters@example.be,,Master,KU Leuven,Informatica,2017-05-15,2023-01-09,,"Platform Engineer",Internal
"Vermeulen, Elke",Active,Elke,,1995-02-14,Female,Gent,Oost-Vlaanderen,9000,Belgium,elke.vermeulen@example.be,,Bachelor,HoGent,Multimedia,2022-02-01,2025-06-02,2026-10-15,"Frontend Consultant",MediaGroup
"Nolens, Frank",Active,Frank,,1987-10-05,Male,Antwerpen,Antwerpen,2000,Belgium,frank.nolens@example.be,,Master,UAntwerpen,Informatica,2018-11-05,2025-03-03,2026-09-30,"Backend Consultant",ACME Manufacturing
"Raman, Gita",Active,Gita,,1996-07-21,Female,Brussel,Brussel,1000,Belgium,gita.raman@example.be,,Master,VUB,Data Science,2023-04-03,2024-04-08,2026-12-31,"Data Engineer",Insura
"Willems, Hugo",Active,Hugo,,1999-03-08,Male,Leuven,Vlaams-Brabant,3000,Belgium,hugo.willems@example.be,,Bachelor,UCLL,Toegepaste Informatica,2024-08-19,2024-08-19,,"DevOps Consultant",
```

`app/sample/bamboo/credits.csv` — a signed ledger, exactly as the real export:

```csv
"Last name, First name","Effective Date",Event,"Event Type",Credits
"Peeters, Dries",2025-01-02,"Nieuw jaar","Nieuw jaar - 2025",100
"Peeters, Dries",2025-02-11,"Tech event bijwonen","Kubernetes Community Days",150
"Peeters, Dries",2025-04-23,"Soft skill event bijwonen","Presenteren voor groepen",40
"Peeters, Dries",2025-06-18,"Afgetekende timesheet tijdig verzonden","Januari - juni 2025",60
"Peeters, Dries",2025-09-30,"Bootcamp","Platform engineering",120
"Peeters, Dries",2025-11-14,"Fun event bijwonen",Personeelsfeest,10
"Peeters, Dries",2025-12-02,"Credits ingeruild","Laptop upgrade",-210
"Peeters, Dries",2026-01-02,"Nieuw jaar","Nieuw jaar - 2026",100
"Peeters, Dries",2026-03-19,"Tech event bijwonen","Open Space Day",30
"Peeters, Dries",2026-07-01,"Tech event bijwonen",AI,50
"Meeus, Ana",2025-01-02,"Nieuw jaar","Nieuw jaar - 2025",100
"Meeus, Ana",2025-05-07,"Tech event bijwonen","Azure Bootcamp",80
"Meeus, Ana",2026-01-02,"Nieuw jaar","Nieuw jaar - 2026",100
"Meeus, Ana",2026-04-15,"Credits ingeruild","Extra verlofdag",-135
"Claes, Bram",2025-01-02,"Nieuw jaar","Nieuw jaar - 2025",100
"Claes, Bram",2025-10-08,"Tech event bijwonen","Techorama",115
"Claes, Bram",2026-01-02,"Nieuw jaar","Nieuw jaar - 2026",100
"Dhondt, Caro",2025-01-02,"Nieuw jaar","Nieuw jaar - 2025",100
"Dhondt, Caro",2025-11-14,"Fun event bijwonen",Personeelsfeest,10
"Dhondt, Caro",2026-01-02,"Nieuw jaar","Nieuw jaar - 2026",100
"Vermeulen, Elke",2025-01-02,"Nieuw jaar","Nieuw jaar - 2025",100
"Vermeulen, Elke",2026-01-02,"Nieuw jaar","Nieuw jaar - 2026",100
"Nolens, Frank",2025-01-02,"Nieuw jaar","Nieuw jaar - 2025",100
"Nolens, Frank",2025-11-14,"Fun event bijwonen",Personeelsfeest,10
"Nolens, Frank",2026-01-02,"Nieuw jaar","Nieuw jaar - 2026",100
"Raman, Gita",2025-01-02,"Nieuw jaar","Nieuw jaar - 2025",100
"Raman, Gita",2026-01-02,"Nieuw jaar","Nieuw jaar - 2026",100
"Willems, Hugo",2026-01-02,"Nieuw jaar","Nieuw jaar - 2026",100
```

> Dries' balance is 100 + 150 + 40 + 60 + 120 + 10 − 210 + 100 + 30 + 50 = **450**, spread
> over ten rows. No chunk says 450. Retrieval returns five of the ten rows and the model
> adds up whatever it was handed, confidently. That is question 5, and no amount of
> hybrid search, reranking or rewriting touches it.

- [ ] **Step 4: Commit**

```bash
git add app/sample
git commit -m "Add synthetic sample corpus reproducing all five demo questions"
```

---

### Task 5: Ingestion

**Files:**
- Create: `app/rag/ingest.py`
- Test: `app/tests/test_ingest.py`

- [ ] **Step 1: Write the failing tests**

`app/tests/test_ingest.py`:

```python
from pathlib import Path

from rag.ingest import ingest_corpus, person_name, swap_name

SAMPLE = Path(__file__).resolve().parents[1] / "sample"


def test_ingests_every_source_type():
    chunks = ingest_corpus(SAMPLE)
    types = {c.source_type for c in chunks}
    assert types == {"policy", "cv", "assignment", "credit", "aggregate"}


def test_person_name_survives_the_real_filename_shapes():
    assert person_name("Itenium - CV Alexander Ryckeboer") == "Alexander Ryckeboer"
    assert person_name("Itenium - CV Bernard Giorgino (FA)") == "Bernard Giorgino"
    assert person_name("Itenium - CV Bert Maes - Business Architect ") == "Bert Maes"
    assert person_name("Itenium - CV Bert Vermorgen - ENG") == "Bert Vermorgen"
    assert (
        person_name("Itenium - CV Bram De Plekker - .NET Angular Cloud Developer - updated")
        == "Bram De Plekker"
    )


def test_swap_name_turns_the_export_order_around():
    assert swap_name("Peeters, Dries") == "Dries Peeters"
    assert swap_name("De Plekker, Bram") == "Bram De Plekker"
    assert swap_name("Madonna") == "Madonna"


def test_assignment_chunks_drop_personal_data():
    chunks = [c for c in ingest_corpus(SAMPLE) if c.source_type == "assignment"]
    joined = "\n".join(c.text for c in chunks)
    for leaked in ("1990-04-11", "Female", "Antwerpen", "2000", "ana.meeus@example.be"):
        assert leaked not in joined
    assert "Klant: RetailCo" in joined


def test_credit_rows_are_one_chunk_each():
    chunks = [c for c in ingest_corpus(SAMPLE) if c.source_type == "credit"]
    assert len(chunks) == 28
    assert all(c.title for c in chunks)


def test_no_credit_chunk_contains_a_balance():
    """Question 5's whole point: the answer is in no retrievable chunk."""
    chunks = [c for c in ingest_corpus(SAMPLE) if c.source_type == "credit"]
    assert all("450" not in c.text for c in chunks)


def test_aggregate_chunk_states_the_summed_balance():
    chunks = [c for c in ingest_corpus(SAMPLE) if c.source_type == "aggregate"]
    dries = next(c for c in chunks if c.title == "Dries Peeters")
    assert "450" in dries.text


def test_aggregates_cover_every_person_in_the_ledger():
    chunks = ingest_corpus(SAMPLE)
    ledger_people = {c.title for c in chunks if c.source_type == "credit"}
    summary_people = {c.title for c in chunks if c.source_type == "aggregate"}
    assert ledger_people == summary_people


def test_cv_chunks_carry_the_person_name_as_title():
    titles = {c.title for c in ingest_corpus(SAMPLE) if c.source_type == "cv"}
    assert {"Dries Peeters", "Bram Claes"} <= titles


def test_policy_chunks_carry_a_heading_path():
    locations = [c.location for c in ingest_corpus(SAMPLE) if c.source_type == "policy"]
    assert any("Opleidingsbudget" in loc for loc in locations)


def test_chunk_ids_are_unique():
    chunks = ingest_corpus(SAMPLE)
    assert len({c.id for c in chunks}) == len(chunks)
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `cd app && uv run pytest tests/test_ingest.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'rag.ingest'`

- [ ] **Step 3: Write the implementation**

`app/rag/ingest.py`:

```python
"""Parse before chunking. Each source type gets the treatment its shape deserves."""

from __future__ import annotations

import csv
import json
import re
from collections import defaultdict
from dataclasses import asdict
from pathlib import Path

from rag.chunking import chunk_id, split_text
from rag.models import Chunk

# Both spellings are supported: `sample/` and the real `data/raw/` use the same names,
# and `policies/` stays accepted so an English-named drop still works.
PROSE_DIRS = [("policy", ["pdfs", "policies"]), ("cv", ["cvs"]), ("project", ["projects"])]

# Date of birth and home address are on the leave-out list in the spec, and no question
# needs them. Dropping at ingest means they never reach the vector store at all.
ASSIGNMENT_DROP = {
    "Birth Date", "Gender", "City", "State", "Zip Code", "Country",
    "Work Email", "LinkedIn URL", "First Name", "Middle Name",
}


def read_document(path: Path) -> str:
    if path.suffix.lower() == ".pdf":
        from pypdf import PdfReader

        return "\n\n".join(page.extract_text() or "" for page in PdfReader(path).pages)
    if path.suffix.lower() == ".docx":
        import docx

        return "\n\n".join(p.text for p in docx.Document(str(path)).paragraphs)
    return path.read_text(encoding="utf-8")


def person_name(filename: str) -> str:
    """Pull the consultant's name out of a CV filename.

    The real exports are named "Itenium - CV Bram De Plekker - .NET Angular Cloud
    Developer - updated.pdf". Everything after the first " - " is role, language or
    revision noise, and a trailing "(FA)" marks a variant of the same person.
    """
    stem = re.sub(r"^itenium\s*-\s*cv\s*", "", filename, flags=re.IGNORECASE)
    stem = stem.split(" - ")[0]
    stem = re.sub(r"\([^)]*\)", "", stem)
    return stem.strip() or filename


def swap_name(name: str) -> str:
    """"Peeters, Dries" -> "Dries Peeters", so records read like the CVs do."""
    if "," not in name:
        return name.strip()
    last, first = name.split(",", 1)
    return f"{first.strip()} {last.strip()}".strip()


def _sections(text: str) -> list[tuple[str, str]]:
    """Split markdown on headings, returning (heading path, body) pairs."""
    doc_title = ""
    sections: list[tuple[str, list[str]]] = []
    current = ""
    body: list[str] = []
    for line in text.splitlines():
        match = re.match(r"^(#{1,6})\s+(.*)$", line)
        if match:
            if body:
                sections.append((current, body))
                body = []
            heading = match.group(2).strip()
            if len(match.group(1)) == 1:
                doc_title = heading
                current = ""
            else:
                current = heading
        else:
            body.append(line)
    if body:
        sections.append((current, body))
    return [
        (f"{doc_title} > {head}" if head else doc_title, "\n".join(lines).strip())
        for head, lines in sections
        if "\n".join(lines).strip()
    ]


def _document_title(text: str, fallback: str) -> str:
    match = re.search(r"^#\s+(.*)$", text, re.MULTILINE)
    if not match:
        return fallback
    # CVs are titled "Name — Role"; the name alone is what a citation should say.
    return match.group(1).split("—")[0].strip()


def _prose_chunks(path: Path, root: Path, source_type: str) -> list[Chunk]:
    text = read_document(path)
    if not text.strip():
        return []
    source = str(path.relative_to(root))
    fallback = person_name(path.stem) if source_type == "cv" else path.stem
    title = _document_title(text, fallback)
    chunks: list[Chunk] = []
    for ordinal, (heading_path, body) in enumerate(_sections(text)):
        for part in split_text(body):
            chunks.append(
                Chunk(
                    id=chunk_id(source, len(chunks), part),
                    text=part,
                    source=source,
                    source_type=source_type,
                    title=title,
                    location=heading_path or title,
                )
            )
    return chunks


def _rows(path: Path) -> list[dict]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def _assignment_chunks(path: Path, root: Path) -> list[Chunk]:
    """One row per assignment, rendered as fields.

    This is the wrong way to index structured data, and that is the point: the records
    come out as near-identical blobs sitting on top of each other in vector space.
    """
    source = str(path.relative_to(root))
    chunks: list[Chunk] = []
    for ordinal, row in enumerate(_rows(path)):
        name = swap_name(row.get("Last name, First name", ""))
        fields = [f"Naam: {name}"] + [
            f"{key}: {value}"
            for key, value in row.items()
            if key and key not in ASSIGNMENT_DROP and key != "Last name, First name" and value
        ]
        text = "\n".join(fields)
        chunks.append(
            Chunk(
                id=chunk_id(source, ordinal, text),
                text=text,
                source=source,
                source_type="assignment",
                title=name,
                location="BambooHR opdracht",
            )
        )
    return chunks


def _credit_chunks(path: Path, root: Path) -> list[Chunk]:
    source = str(path.relative_to(root))
    chunks: list[Chunk] = []
    for ordinal, row in enumerate(_rows(path)):
        name = swap_name(row.get("Last name, First name", ""))
        text = (
            f"Naam: {name}\n"
            f"Datum: {row.get('Effective Date', '')}\n"
            f"Event: {row.get('Event', '')}\n"
            f"Type: {row.get('Event Type', '')}\n"
            f"Credits: {row.get('Credits', '')}"
        )
        chunks.append(
            Chunk(
                id=chunk_id(source, ordinal, text),
                text=text,
                source=source,
                source_type="credit",
                title=name,
                location=f"Creditsboeking {row.get('Effective Date', '')}",
            )
        )
    return chunks


def _credit_aggregate_chunks(path: Path, root: Path) -> list[Chunk]:
    """The answer, computed at ingest time.

    Nothing here is a retrieval technique. Summing a ledger is arithmetic over records,
    which is exactly what vector search cannot do — so it happens before the vectors
    exist. Hidden until wizard step 6.
    """
    source = str(path.relative_to(root))
    earned: dict[str, float] = defaultdict(float)
    spent: dict[str, float] = defaultdict(float)
    events: dict[str, int] = defaultdict(int)
    latest: dict[str, str] = defaultdict(str)

    for row in _rows(path):
        name = swap_name(row.get("Last name, First name", ""))
        try:
            credits = float(row.get("Credits") or 0)
        except ValueError:
            continue
        (earned if credits >= 0 else spent)[name] += credits
        events[name] += 1
        latest[name] = max(latest[name], row.get("Effective Date") or "")

    chunks: list[Chunk] = []
    for ordinal, name in enumerate(sorted(events)):
        balance = earned[name] + spent[name]
        text = (
            f"Creditsaldo voor {name}.\n"
            f"Huidig saldo: {balance:g} credits.\n"
            f"Verdiend: {earned[name]:g}. Ingeruild: {abs(spent[name]):g}.\n"
            f"Aantal boekingen: {events[name]}. Laatste boeking: {latest[name] or 'onbekend'}."
        )
        chunks.append(
            Chunk(
                id=chunk_id(f"{source}#aggregate", ordinal, text),
                text=text,
                source=source,
                source_type="aggregate",
                title=name,
                location="Berekend creditsaldo",
            )
        )
    return chunks


def _bamboo_dir(root: Path) -> Path | None:
    directory = root / "bamboo"
    return directory if directory.is_dir() else None


def ingest_corpus(root: Path) -> list[Chunk]:
    root = Path(root)
    chunks: list[Chunk] = []

    for source_type, names in PROSE_DIRS:
        for name in names:
            directory = root / name
            if not directory.is_dir():
                continue
            for path in sorted(directory.iterdir()):
                if path.suffix.lower() in {".md", ".txt", ".pdf", ".docx"}:
                    chunks.extend(_prose_chunks(path, root, source_type))

    bamboo = _bamboo_dir(root)
    if bamboo:
        for path in sorted(bamboo.glob("*.csv")):
            if "credit" in path.stem.lower():
                chunks.extend(_credit_chunks(path, root))
                chunks.extend(_credit_aggregate_chunks(path, root))
            else:
                chunks.extend(_assignment_chunks(path, root))

    return chunks


def write_chunks(chunks: list[Chunk], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for chunk in chunks:
            handle.write(json.dumps(asdict(chunk), ensure_ascii=False) + "\n")


def read_chunks(path: Path) -> list[Chunk]:
    with Path(path).open(encoding="utf-8") as handle:
        return [Chunk(**json.loads(line)) for line in handle if line.strip()]
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `cd app && uv run pytest tests/test_ingest.py -v`
Expected: 11 passed

- [ ] **Step 5: Commit**

```bash
git add app/rag/ingest.py app/tests/test_ingest.py
git commit -m "Add corpus ingestion with per-source-type chunking and credit aggregates"
```

---

### Task 6: Dense and sparse indexes

**Files:**
- Create: `app/rag/index.py`
- Test: `app/tests/test_index.py`

- [ ] **Step 1: Write the failing tests**

`app/tests/test_index.py`:

```python
import numpy as np

from rag.index import Bm25Index, DenseIndex, tokenize
from rag.models import Chunk


def _chunk(cid: str, text: str) -> Chunk:
    return Chunk(id=cid, text=text, source="s", source_type="cv", title=cid, location="l")


def test_tokenizer_keeps_certification_codes_whole():
    assert "az-204" in tokenize("Holds the AZ-204 certification")
    assert "az-104" not in tokenize("Holds the AZ-204 certification")


def test_bm25_matches_the_exact_code_only():
    chunks = [
        _chunk("a", "Certifications: AZ-104 and AZ-400 for Azure administration"),
        _chunk("b", "Certifications: AZ-204 Developing Solutions for Microsoft Azure"),
        _chunk("c", "Certifications: DP-203 Data Engineering on Microsoft Azure"),
    ]
    hits = Bm25Index(chunks).search("Who has the AZ-204 certification?", k=3)
    assert hits[0][0].id == "b"


def test_bm25_keeps_a_match_whose_idf_is_zero():
    # rank_bm25 gives a term appearing in exactly half the corpus an idf of 0.0, so
    # every score is 0.0 and a score filter would throw the real match away.
    chunks = [_chunk("a", "kubernetes platform"), _chunk("b", "angular frontend")]
    hits = Bm25Index(chunks).search("kubernetes", k=5)
    assert [c.id for c, _ in hits] == ["a"]
    assert hits[0][1] == 0.0


def test_bm25_returns_nothing_when_no_chunk_shares_a_term():
    chunks = [_chunk("a", "kubernetes platform"), _chunk("b", "angular frontend")]
    assert Bm25Index(chunks).search("terraform", k=5) == []


def test_dense_returns_nearest_first():
    chunks = [_chunk("a", "x"), _chunk("b", "y"), _chunk("c", "z")]
    vectors = np.array([[1.0, 0.0], [0.0, 1.0], [0.7071, 0.7071]], dtype=np.float32)
    hits = DenseIndex(chunks, vectors).search(np.array([1.0, 0.0], dtype=np.float32), k=3)
    assert [c.id for c, _ in hits] == ["a", "c", "b"]
    assert hits[0][1] > hits[1][1] > hits[2][1]


def test_dense_respects_k():
    chunks = [_chunk("a", "x"), _chunk("b", "y")]
    vectors = np.array([[1.0, 0.0], [0.0, 1.0]], dtype=np.float32)
    assert len(DenseIndex(chunks, vectors).search(np.array([1.0, 0.0], dtype=np.float32), k=1)) == 1
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `cd app && uv run pytest tests/test_index.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'rag.index'`

- [ ] **Step 3: Write the implementation**

`app/rag/index.py`:

```python
from __future__ import annotations

import re

import numpy as np
from rank_bm25 import BM25Okapi

from rag.models import Chunk

# Hyphens and dots stay inside a token so `az-204` survives as one term. Splitting it
# into `az` + `204` would let AZ-104 match half the query, which is the failure hybrid
# search is supposed to fix.
TOKEN = re.compile(r"[a-z0-9][a-z0-9._-]*")


def tokenize(text: str) -> list[str]:
    return TOKEN.findall(text.lower())


class DenseIndex:
    """Brute-force cosine similarity. A few thousand vectors is a millisecond."""

    def __init__(self, chunks: list[Chunk], vectors: np.ndarray) -> None:
        if len(chunks) != len(vectors):
            raise ValueError(f"{len(chunks)} chunks but {len(vectors)} vectors")
        self.chunks = chunks
        self.vectors = vectors.astype(np.float32)

    def search(self, query_vector: np.ndarray, k: int) -> list[tuple[Chunk, float]]:
        scores = self.vectors @ query_vector.astype(np.float32)
        top = np.argsort(-scores)[:k]
        return [(self.chunks[i], float(scores[i])) for i in top]


class Bm25Index:
    def __init__(self, chunks: list[Chunk]) -> None:
        self.chunks = chunks
        self._tokens = [set(tokenize(c.text)) for c in chunks]
        self._bm25 = BM25Okapi([tokenize(c.text) for c in chunks])

    def search(self, query: str, k: int) -> list[tuple[Chunk, float]]:
        tokens = tokenize(query)
        scores = self._bm25.get_scores(tokens)
        top = np.argsort(-scores)[:k]
        # Discarding on `score > 0` would be wrong. rank_bm25 computes
        # idf = log(N - f + 0.5) - log(f + 0.5), which is exactly zero for a term in
        # half the corpus, so a real match can score 0.0 and become indistinguishable
        # from no match at all. Whether the chunk contains a query term is the actual
        # question, and it is the one worth asking.
        wanted = set(tokens)
        return [
            (self.chunks[i], float(scores[i])) for i in top if wanted & self._tokens[i]
        ]
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `cd app && uv run pytest tests/test_index.py -v`
Expected: 6 passed

- [ ] **Step 5: Commit**

```bash
git add app/rag/index.py app/tests/test_index.py
git commit -m "Add dense and BM25 indexes"
```

---

### Task 7: Reciprocal rank fusion

**Files:**
- Create: `app/rag/fuse.py`
- Test: `app/tests/test_fuse.py`

- [ ] **Step 1: Write the failing tests**

`app/tests/test_fuse.py`:

```python
from rag.fuse import reciprocal_rank_fusion
from rag.models import Chunk


def _chunk(cid: str) -> Chunk:
    return Chunk(id=cid, text=cid, source="s", source_type="cv", title=cid, location="l")


A, B, C = _chunk("a"), _chunk("b"), _chunk("c")


def test_chunk_found_by_both_retrievers_beats_one_found_by_one():
    fused = reciprocal_rank_fusion({"dense": [A, B], "bm25": [B]})
    assert [s.chunk.id for s in fused] == ["b", "a"]


def test_first_and_third_beats_second_and_second():
    # RRF is convex in rank: 1/(k+1) + 1/(k+3) > 2/(k+2). A chunk one retriever loves
    # and the other dislikes outranks one that both merely tolerate. Surprising, and
    # the reason RRF does not just average ranks.
    fused = reciprocal_rank_fusion({"dense": [A, B, C], "bm25": [C, B, A]})
    assert fused[-1].chunk.id == "b"


def test_ranks_record_the_position_in_each_retriever():
    fused = reciprocal_rank_fusion({"dense": [A, B], "bm25": [B, A]})
    by_id = {s.chunk.id: s for s in fused}
    assert by_id["a"].ranks == {"dense": 1, "bm25": 2}
    assert by_id["b"].ranks == {"dense": 2, "bm25": 1}


def test_chunk_found_by_one_retriever_only_still_appears():
    fused = reciprocal_rank_fusion({"dense": [A], "bm25": [B]})
    assert {s.chunk.id for s in fused} == {"a", "b"}
    assert all(len(s.ranks) == 1 for s in fused)


def test_single_retriever_preserves_its_order():
    fused = reciprocal_rank_fusion({"dense": [A, B, C]})
    assert [s.chunk.id for s in fused] == ["a", "b", "c"]


def test_scores_descend():
    fused = reciprocal_rank_fusion({"dense": [A, B, C], "bm25": [C, B, A]})
    scores = [s.score for s in fused]
    assert scores == sorted(scores, reverse=True)
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `cd app && uv run pytest tests/test_fuse.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'rag.fuse'`

- [ ] **Step 3: Write the implementation**

`app/rag/fuse.py`:

```python
"""Reciprocal rank fusion — the ten-line merge that surprises people."""

from __future__ import annotations

from rag.models import Chunk, Scored

# The constant damps the influence of top ranks so one retriever cannot dominate;
# 60 is the value from the original RRF paper and nobody has found better.
RRF_K = 60


def reciprocal_rank_fusion(
    rankings: dict[str, list[Chunk]], *, k: int = RRF_K
) -> list[Scored]:
    scores: dict[str, float] = {}
    ranks: dict[str, dict[str, int]] = {}
    chunks: dict[str, Chunk] = {}

    for retriever, ranked in rankings.items():
        for position, chunk in enumerate(ranked, start=1):
            chunks[chunk.id] = chunk
            scores[chunk.id] = scores.get(chunk.id, 0.0) + 1.0 / (k + position)
            ranks.setdefault(chunk.id, {})[retriever] = position

    ordered = sorted(scores, key=lambda cid: -scores[cid])
    return [Scored(chunks[cid], scores[cid], ranks[cid]) for cid in ordered]
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `cd app && uv run pytest tests/test_fuse.py -v`
Expected: 6 passed

- [ ] **Step 5: Commit**

```bash
git add app/rag/fuse.py app/tests/test_fuse.py
git commit -m "Add reciprocal rank fusion"
```

---

### Task 8: Embeddings and reranking

**Files:**
- Create: `app/rag/embed.py`
- Create: `app/rag/rerank.py`
- Test: `app/tests/test_rerank.py`

- [ ] **Step 1: Write the failing test**

`app/tests/test_rerank.py`:

```python
from rag.fuse import reciprocal_rank_fusion
from rag.models import Chunk
from rag.rerank import apply_rerank


class FakeReranker:
    """Scores by how many times the query word appears — enough to prove reordering."""

    def score(self, query: str, texts: list[str]) -> list[float]:
        return [float(t.lower().count(query.lower())) for t in texts]


def _chunk(cid: str, text: str) -> Chunk:
    return Chunk(id=cid, text=text, source="s", source_type="cv", title=cid, location="l")


def test_rerank_reorders_and_truncates():
    candidates = reciprocal_rank_fusion(
        {"dense": [_chunk("a", "x"), _chunk("b", "x x x"), _chunk("c", "x x")]}
    )
    top = apply_rerank(FakeReranker(), "x", candidates, top_n=2)
    assert [s.chunk.id for s in top] == ["b", "c"]


def test_rerank_records_both_ranks():
    candidates = reciprocal_rank_fusion(
        {"dense": [_chunk("a", "x"), _chunk("b", "x x x")]}
    )
    top = apply_rerank(FakeReranker(), "x", candidates, top_n=2)
    # b was second out of retrieval and first after reranking — this delta is the demo.
    assert top[0].ranks["dense"] == 2
    assert top[0].ranks["rerank"] == 1
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `cd app && uv run pytest tests/test_rerank.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'rag.rerank'`

- [ ] **Step 3: Write the implementations**

`app/rag/embed.py`:

```python
"""Local embeddings. Nothing leaves the machine, and the model is small enough to be fast."""

from __future__ import annotations

import functools

import numpy as np

# The corpus is Dutch (arbeidsreglement, opleidingsplan, kilometervergoeding) and English
# (CVs, AI policy) in one index, and a Dutch question has to reach an English CV. An
# English-only model would fail every question for the wrong reason.
MODEL_NAME = "intfloat/multilingual-e5-small"
# e5 requires these prefixes and is measurably worse without them. Asymmetric on
# purpose: a question and the passage answering it are different kinds of text.
QUERY_PREFIX = "query: "
PASSAGE_PREFIX = "passage: "


@functools.lru_cache(maxsize=1)
def _model():
    from sentence_transformers import SentenceTransformer

    return SentenceTransformer(MODEL_NAME)


def embed_passages(texts: list[str]) -> np.ndarray:
    return _model().encode(
        [PASSAGE_PREFIX + t for t in texts],
        normalize_embeddings=True,
        show_progress_bar=True,
    ).astype(np.float32)


def embed_query(text: str) -> np.ndarray:
    return _model().encode(
        [QUERY_PREFIX + text], normalize_embeddings=True
    ).astype(np.float32)[0]
```

`app/rag/rerank.py`:

```python
from __future__ import annotations

import functools
from typing import Protocol

from rag.models import Scored

# Multilingual, to match the embedding model.
MODEL_NAME = "BAAI/bge-reranker-v2-m3"


class Reranker(Protocol):
    def score(self, query: str, texts: list[str]) -> list[float]: ...


class CrossEncoderReranker:
    def score(self, query: str, texts: list[str]) -> list[float]:
        pairs = [(query, text) for text in texts]
        return [float(s) for s in _model().predict(pairs)]


@functools.lru_cache(maxsize=1)
def _model():
    from sentence_transformers import CrossEncoder

    return CrossEncoder(MODEL_NAME)


def apply_rerank(
    reranker: Reranker, query: str, candidates: list[Scored], *, top_n: int
) -> list[Scored]:
    if not candidates:
        return []
    scores = reranker.score(query, [c.chunk.text for c in candidates])
    ordered = sorted(zip(candidates, scores), key=lambda pair: -pair[1])
    return [
        Scored(candidate.chunk, score, {**candidate.ranks, "rerank": position})
        for position, (candidate, score) in enumerate(ordered[:top_n], start=1)
    ]
```

- [ ] **Step 4: Run the test to verify it passes**

Run: `cd app && uv run pytest tests/test_rerank.py -v`
Expected: 2 passed

- [ ] **Step 5: Commit**

```bash
git add app/rag/embed.py app/rag/rerank.py app/tests/test_rerank.py
git commit -m "Add local embedding and cross-encoder reranking"
```

---

### Task 9: LLM protocol and disk cache

**Files:**
- Create: `app/rag/llm.py`
- Test: `app/tests/test_llm.py`

- [ ] **Step 1: Write the failing tests**

`app/tests/test_llm.py`:

```python
import pytest

from rag.llm import CachedLLM, NoAnswerAvailable


class CountingLLM:
    def __init__(self, reply: str = "answer") -> None:
        self.reply = reply
        self.calls = 0

    def complete(self, system: str, prompt: str) -> str:
        self.calls += 1
        return self.reply


def test_second_identical_call_is_served_from_cache(tmp_path):
    inner = CountingLLM()
    llm = CachedLLM(inner, tmp_path)
    assert llm.complete("sys", "prompt") == "answer"
    assert llm.complete("sys", "prompt") == "answer"
    assert inner.calls == 1


def test_different_prompt_is_a_different_entry(tmp_path):
    inner = CountingLLM()
    llm = CachedLLM(inner, tmp_path)
    llm.complete("sys", "one")
    llm.complete("sys", "two")
    assert inner.calls == 2


def test_cache_survives_a_new_process(tmp_path):
    CachedLLM(CountingLLM(), tmp_path).complete("sys", "prompt")
    inner = CountingLLM()
    assert CachedLLM(inner, tmp_path).complete("sys", "prompt") == "answer"
    assert inner.calls == 0


def test_offline_mode_serves_cache_and_refuses_a_miss(tmp_path):
    CachedLLM(CountingLLM(), tmp_path).complete("sys", "hit")
    offline = CachedLLM(None, tmp_path)
    assert offline.complete("sys", "hit") == "answer"
    with pytest.raises(NoAnswerAvailable):
        offline.complete("sys", "miss")


def test_upstream_failure_falls_back_to_any_cached_answer(tmp_path):
    class Broken:
        def complete(self, system: str, prompt: str) -> str:
            raise RuntimeError("api down")

    CachedLLM(CountingLLM("earlier"), tmp_path).complete("sys", "hit")
    llm = CachedLLM(Broken(), tmp_path)
    assert llm.complete("sys", "miss", fallback_to="hit") == "earlier"
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `cd app && uv run pytest tests/test_llm.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'rag.llm'`

- [ ] **Step 3: Write the implementation**

`app/rag/llm.py`:

```python
"""The only part of the pipeline that touches the network, and it is cached.

Keying on (system, prompt) rather than on (question, config) is deliberate: two configs
that produce the same prompt should share a cache entry, and a prompt edit should not
silently reuse an answer written for the previous wording.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Protocol

MODEL = "claude-opus-5"
MAX_TOKENS = 2048


class NoAnswerAvailable(RuntimeError):
    """Cache miss with no way to reach the model."""


class LLM(Protocol):
    def complete(self, system: str, prompt: str) -> str: ...


class AnthropicLLM:
    """Zero-arg client: it resolves the OAuth profile written by `ant auth login`."""

    def __init__(self) -> None:
        from anthropic import Anthropic

        self._client = Anthropic()

    def complete(self, system: str, prompt: str) -> str:
        message = self._client.messages.create(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            system=system,
            messages=[{"role": "user", "content": prompt}],
        )
        return "".join(b.text for b in message.content if b.type == "text")


def cache_key(system: str, prompt: str) -> str:
    payload = json.dumps({"system": system, "prompt": prompt}, sort_keys=True)
    return hashlib.sha256(payload.encode()).hexdigest()[:32]


class CachedLLM:
    def __init__(self, inner: LLM | None, cache_dir: Path) -> None:
        self._inner = inner
        self._dir = Path(cache_dir)
        self._dir.mkdir(parents=True, exist_ok=True)

    def _path(self, system: str, prompt: str) -> Path:
        return self._dir / f"{cache_key(system, prompt)}.json"

    def _read(self, system: str, prompt: str) -> str | None:
        path = self._path(system, prompt)
        if not path.is_file():
            return None
        return json.loads(path.read_text(encoding="utf-8"))["response"]

    def complete(self, system: str, prompt: str, *, fallback_to: str | None = None) -> str:
        cached = self._read(system, prompt)
        if cached is not None:
            return cached

        if self._inner is None:
            raise NoAnswerAvailable(
                "No cached answer and no credential. Run scripts/warm_cache.py, "
                "or `ant auth login` to enable live calls."
            )

        try:
            response = self._inner.complete(system, prompt)
        except Exception:
            # On stage, a stale answer beats a stack trace.
            if fallback_to is not None:
                stale = self._read(system, fallback_to)
                if stale is not None:
                    return stale
            raise

        self._path(system, prompt).write_text(
            json.dumps({"system": system, "prompt": prompt, "response": response}),
            encoding="utf-8",
        )
        return response


def build_llm(cache_dir: Path) -> CachedLLM:
    try:
        inner: LLM | None = AnthropicLLM()
    except Exception:
        inner = None
    return CachedLLM(inner, cache_dir)
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `cd app && uv run pytest tests/test_llm.py -v`
Expected: 5 passed

- [ ] **Step 5: Commit**

```bash
git add app/rag/llm.py app/tests/test_llm.py
git commit -m "Add LLM protocol with disk cache and on-stage fallback"
```

---

### Task 10: Query rewriting and answer generation

**Files:**
- Create: `app/rag/rewrite.py`
- Create: `app/rag/generate.py`
- Test: `app/tests/test_generate.py`

- [ ] **Step 1: Write the failing tests**

`app/tests/test_generate.py`:

```python
from rag.fuse import reciprocal_rank_fusion
from rag.generate import extract_citations, generate_answer
from rag.models import Chunk
from rag.rewrite import rewrite_query


class ScriptedLLM:
    def __init__(self, reply: str) -> None:
        self.reply = reply
        self.last_prompt = ""

    def complete(self, system: str, prompt: str, **kwargs) -> str:
        self.last_prompt = prompt
        return self.reply


def _chunk(cid: str, text: str) -> Chunk:
    return Chunk(id=cid, text=text, source="s", source_type="cv", title=cid, location="Section")


def test_rewrite_returns_the_broadened_question():
    llm = ScriptedLLM("Which consultants are available and what does ACME need?")
    assert rewrite_query(llm, "Who can take over ACME in October?").startswith("Which")


def test_rewrite_passes_the_original_question_through():
    llm = ScriptedLLM("broadened")
    rewrite_query(llm, "Who has AZ-204?")
    assert "Who has AZ-204?" in llm.last_prompt


def test_rewrite_falls_back_to_the_original_on_an_empty_reply():
    assert rewrite_query(ScriptedLLM("  "), "original") == "original"


def test_generate_numbers_the_sources_in_the_prompt():
    llm = ScriptedLLM("The budget is EUR 2000 [1].")
    candidates = reciprocal_rank_fusion({"dense": [_chunk("a", "budget is EUR 2000")]})
    generate_answer(llm, "What is the budget?", candidates)
    assert "[1]" in llm.last_prompt
    assert "budget is EUR 2000" in llm.last_prompt


def test_extract_citations_maps_markers_to_chunks():
    candidates = reciprocal_rank_fusion(
        {"dense": [_chunk("a", "first"), _chunk("b", "second")]}
    )
    citations = extract_citations("Claim one [1]. Claim two [2].", candidates)
    assert [c.marker for c in citations] == [1, 2]
    assert [c.chunk_id for c in citations] == ["a", "b"]


def test_extract_citations_ignores_markers_with_no_source():
    candidates = reciprocal_rank_fusion({"dense": [_chunk("a", "first")]})
    assert extract_citations("Claim [7].", candidates) == []


def test_extract_citations_deduplicates():
    candidates = reciprocal_rank_fusion({"dense": [_chunk("a", "first")]})
    assert len(extract_citations("A [1]. B [1].", candidates)) == 1
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `cd app && uv run pytest tests/test_generate.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'rag.generate'`

- [ ] **Step 3: Write the implementations**

`app/rag/rewrite.py`:

```python
"""Step-back prompting: the question as typed is often a bad search query."""

from __future__ import annotations

SYSTEM = """You rewrite questions into better search queries for a document search over
consultant CVs, project sheets, HR records and company policies.

Broaden an over-specific question into the more general one that has to be answered
first. Split a compound question into its parts. Keep every proper noun, product name
and certification code from the original exactly as written.

Reply with the rewritten query and nothing else."""


def rewrite_query(llm, question: str) -> str:
    rewritten = llm.complete(SYSTEM, f"Question: {question}").strip()
    return rewritten or question
```

`app/rag/generate.py`:

```python
from __future__ import annotations

import re

from rag.models import Citation, Scored

SYSTEM = """You answer questions about a consultancy from the numbered sources supplied.

Use only what the sources say. Cite every claim with the source number in square
brackets, like [2]. If the sources do not contain the answer, say so plainly and stop —
a refusal is more useful than a guess."""

MARKER = re.compile(r"\[(\d+)\]")


def _format_sources(candidates: list[Scored]) -> str:
    return "\n\n".join(
        f"[{i}] {s.chunk.title} — {s.chunk.location}\n{s.chunk.text}"
        for i, s in enumerate(candidates, start=1)
    )


def generate_answer(llm, question: str, candidates: list[Scored], **kwargs) -> str:
    if not candidates:
        return "Nothing in the corpus matched that question."
    prompt = f"Sources:\n\n{_format_sources(candidates)}\n\nQuestion: {question}"
    return llm.complete(SYSTEM, prompt, **kwargs).strip()


def extract_citations(answer: str, candidates: list[Scored]) -> list[Citation]:
    citations: list[Citation] = []
    seen: set[int] = set()
    for match in MARKER.finditer(answer):
        marker = int(match.group(1))
        if marker in seen or not 1 <= marker <= len(candidates):
            continue
        seen.add(marker)
        chunk = candidates[marker - 1].chunk
        citations.append(
            Citation(
                marker=marker,
                chunk_id=chunk.id,
                title=chunk.title,
                location=chunk.location,
            )
        )
    return citations
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `cd app && uv run pytest tests/test_generate.py -v`
Expected: 7 passed

- [ ] **Step 5: Commit**

```bash
git add app/rag/rewrite.py app/rag/generate.py app/tests/test_generate.py
git commit -m "Add step-back query rewriting and cited answer generation"
```

---

### Task 11: The engine

**Files:**
- Create: `app/rag/pipeline.py`
- Test: `app/tests/test_pipeline.py`

- [ ] **Step 1: Write the failing tests**

`app/tests/test_pipeline.py`:

```python
import numpy as np

from rag.index import Bm25Index, DenseIndex
from rag.models import Config, Chunk
from rag.pipeline import Engine


class StubLLM:
    def __init__(self) -> None:
        self.prompts: list[str] = []

    def complete(self, system: str, prompt: str, **kwargs) -> str:
        self.prompts.append(prompt)
        return "rewritten query" if "Question:" in prompt and "Sources:" not in prompt else "An answer [1]."


class WordCountReranker:
    def score(self, query: str, texts: list[str]) -> list[float]:
        return [float(len(t.split())) for t in texts]


def _chunk(cid: str, text: str) -> Chunk:
    return Chunk(id=cid, text=text, source="s", source_type="cv", title=cid, location="l")


def _engine(llm=None):
    chunks = [
        _chunk("a", "AZ-104 and AZ-400 azure administration"),
        _chunk("b", "AZ-204 developing solutions for microsoft azure"),
        _chunk("c", "kubernetes platform engineering with many many many words here"),
    ]
    vectors = np.array([[1.0, 0.0], [0.9, 0.436], [0.0, 1.0]], dtype=np.float32)
    return Engine(
        dense=DenseIndex(chunks, vectors),
        bm25=Bm25Index(chunks),
        reranker=WordCountReranker(),
        llm=llm or StubLLM(),
        embed_query=lambda _: np.array([1.0, 0.0], dtype=np.float32),
    )


def test_dense_only_never_consults_bm25():
    result = _engine().run("AZ-204", Config(top_n=2))
    assert all("bm25" not in s.ranks for s in result.candidates)


def test_hybrid_records_both_retrievers():
    result = _engine().run("AZ-204", Config(bm25=True, top_n=3))
    assert any("bm25" in s.ranks for s in result.candidates)


def test_rerank_populates_the_rerank_rank():
    result = _engine().run("kubernetes", Config(bm25=True, rerank=True, top_n=2))
    assert all("rerank" in s.ranks for s in result.used)


def test_used_is_capped_at_top_n():
    result = _engine().run("azure", Config(bm25=True, top_n=2))
    assert len(result.used) == 2


def test_rewrite_off_leaves_rewritten_none():
    assert _engine().run("AZ-204", Config()).rewritten is None


def test_rewrite_on_sets_rewritten_and_searches_with_it():
    result = _engine().run("AZ-204", Config(rewrite=True, top_n=2))
    assert result.rewritten == "rewritten query"


def test_aggregate_chunks_are_hidden_until_enabled():
    chunks = [
        _chunk("a", "AZ-104 and AZ-400 azure administration"),
        Chunk(id="agg", text="Current balance: 340 credits", source="s",
              source_type="aggregate", title="Dries", location="summary"),
    ]
    vectors = np.array([[1.0, 0.0], [1.0, 0.0]], dtype=np.float32)
    engine = Engine(
        dense=DenseIndex(chunks, vectors),
        bm25=Bm25Index(chunks),
        reranker=WordCountReranker(),
        llm=StubLLM(),
        embed_query=lambda _: np.array([1.0, 0.0], dtype=np.float32),
    )
    hidden = engine.run("credits", Config(top_n=5))
    assert all(s.chunk.source_type != "aggregate" for s in hidden.used)
    shown = engine.run("credits", Config(aggregates=True, top_n=5))
    assert any(s.chunk.source_type == "aggregate" for s in shown.used)


def test_citations_only_extracted_when_enabled():
    assert _engine().run("azure", Config(top_n=2)).citations == []
    with_citations = _engine().run("azure", Config(citations=True, top_n=2))
    assert with_citations.citations[0].marker == 1
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `cd app && uv run pytest tests/test_pipeline.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'rag.pipeline'`

- [ ] **Step 3: Write the implementation**

`app/rag/pipeline.py`:

```python
"""The whole pipeline. This is the module that goes on a slide — keep it readable."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import numpy as np

from rag.fuse import reciprocal_rank_fusion
from rag.generate import extract_citations, generate_answer
from rag.index import Bm25Index, DenseIndex
from rag.models import Chunk, Config, Result, Scored
from rag.rerank import Reranker, apply_rerank
from rag.rewrite import rewrite_query


@dataclass
class Engine:
    dense: DenseIndex
    bm25: Bm25Index
    reranker: Reranker
    llm: object
    embed_query: Callable[[str], np.ndarray]

    def retrieve(self, query: str, config: Config) -> list[Scored]:
        def visible(hits) -> list[Chunk]:
            return [
                chunk
                for chunk, _ in hits
                if config.aggregates or chunk.source_type != "aggregate"
            ]

        rankings: dict[str, list[Chunk]] = {}
        if config.dense:
            rankings["dense"] = visible(self.dense.search(self.embed_query(query), config.top_k))
        if config.bm25:
            rankings["bm25"] = visible(self.bm25.search(query, config.top_k))
        return reciprocal_rank_fusion(rankings)

    def run(self, question: str, config: Config) -> Result:
        query = question
        rewritten = None
        if config.rewrite:
            rewritten = rewrite_query(self.llm, question)
            query = rewritten

        candidates = self.retrieve(query, config)

        if config.rerank:
            used = apply_rerank(self.reranker, query, candidates, top_n=config.top_n)
        else:
            used = candidates[: config.top_n]

        answer = generate_answer(self.llm, question, used, fallback_to=question)
        citations = extract_citations(answer, used) if config.citations else []

        return Result(
            question=question,
            rewritten=rewritten,
            candidates=candidates,
            used=used,
            answer=answer,
            citations=citations,
        )
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `cd app && uv run pytest tests/test_pipeline.py -v`
Expected: 8 passed

- [ ] **Step 5: Commit**

```bash
git add app/rag/pipeline.py app/tests/test_pipeline.py
git commit -m "Add the pipeline engine driven by Config presets"
```

---

### Task 12: Index building

**Files:**
- Create: `app/rag/store.py`
- Create: `app/scripts/build_index.py`
- Test: `app/tests/test_store.py`

- [ ] **Step 1: Write the failing test**

`app/tests/test_store.py`:

```python
import numpy as np

from rag.models import Chunk
from rag.store import load_artefacts, save_artefacts


def _chunk(cid: str) -> Chunk:
    return Chunk(id=cid, text=cid, source="s", source_type="cv", title=cid, location="l")


def test_round_trip_preserves_chunks_and_vectors(tmp_path):
    chunks = [_chunk("a"), _chunk("b")]
    vectors = np.array([[1.0, 0.0], [0.0, 1.0]], dtype=np.float32)
    projection = np.array([[0.1, 0.2], [0.3, 0.4]], dtype=np.float32)
    save_artefacts(tmp_path, chunks, vectors, projection)

    loaded_chunks, loaded_vectors, loaded_projection = load_artefacts(tmp_path)
    assert [c.id for c in loaded_chunks] == ["a", "b"]
    assert np.allclose(loaded_vectors, vectors)
    assert np.allclose(loaded_projection, projection)


def test_missing_artefacts_name_the_file_and_the_fix(tmp_path):
    import pytest

    with pytest.raises(FileNotFoundError, match="build_index"):
        load_artefacts(tmp_path)
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `cd app && uv run pytest tests/test_store.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'rag.store'`

- [ ] **Step 3: Write the implementation**

`app/rag/store.py`:

```python
from __future__ import annotations

from pathlib import Path

import numpy as np

from rag.ingest import read_chunks, write_chunks
from rag.models import Chunk

CHUNKS = "chunks.jsonl"
EMBEDDINGS = "embeddings.npy"
PROJECTION = "projection.npy"


def save_artefacts(
    directory: Path, chunks: list[Chunk], vectors: np.ndarray, projection: np.ndarray
) -> None:
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    write_chunks(chunks, directory / CHUNKS)
    np.save(directory / EMBEDDINGS, vectors)
    np.save(directory / PROJECTION, projection)


def load_artefacts(directory: Path) -> tuple[list[Chunk], np.ndarray, np.ndarray]:
    directory = Path(directory)
    for name in (CHUNKS, EMBEDDINGS, PROJECTION):
        if not (directory / name).exists():
            raise FileNotFoundError(
                f"{directory / name} is missing. Run: uv run python scripts/build_index.py"
            )
    return (
        read_chunks(directory / CHUNKS),
        np.load(directory / EMBEDDINGS),
        np.load(directory / PROJECTION),
    )
```

`app/scripts/build_index.py`:

```python
"""Build every artefact the app loads at startup. Run once, before the talk."""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np

APP = Path(__file__).resolve().parents[1]


def project(vectors: np.ndarray) -> np.ndarray:
    import umap

    # A fixed seed so the map looks the same in rehearsal as it does on the day.
    reducer = umap.UMAP(n_components=2, metric="cosine", random_state=42)
    return reducer.fit_transform(vectors).astype(np.float32)


def main() -> None:
    import sys

    sys.path.insert(0, str(APP))
    from rag.embed import embed_passages
    from rag.ingest import ingest_corpus
    from rag.store import save_artefacts

    parser = argparse.ArgumentParser()
    parser.add_argument("--corpus", type=Path, default=None)
    parser.add_argument("--out", type=Path, default=APP / "data" / "index")
    args = parser.parse_args()

    corpus = args.corpus or (
        APP / "data" / "raw" if (APP / "data" / "raw").is_dir() else APP / "sample"
    )
    print(f"Ingesting {corpus}")
    chunks = ingest_corpus(corpus)
    if not chunks:
        raise SystemExit(
            f"No documents found under {corpus}. Expected policies/, projects/, cvs/ "
            "or bamboo.json."
        )
    print(f"{len(chunks)} chunks")

    vectors = embed_passages([c.text for c in chunks])
    projection = project(vectors)
    save_artefacts(args.out, chunks, vectors, projection)
    print(f"Wrote artefacts to {args.out}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run the test, then build the sample index**

```bash
cd app
uv run pytest tests/test_store.py -v
uv run python scripts/build_index.py --corpus sample --out data/index
```

Expected: 2 passed, then a first run that downloads `bge-small-en-v1.5` and prints a chunk count and the output path.

- [ ] **Step 5: Commit**

```bash
git add app/rag/store.py app/scripts/build_index.py app/tests/test_store.py
git commit -m "Add artefact store and index building script"
```

---

### Task 13: The scoreboard test

This is the task that protects the talk. Everything before it tested components; this tests the claim the session makes.

**Files:**
- Create: `app/questions.yaml`
- Create: `app/rag/app.py`
- Test: `app/tests/test_scoreboard.py`

- [ ] **Step 1: Write the questions file**

`app/questions.yaml`:

```yaml
# Each question's expected verdict at each wizard step. The check is on retrieval, not
# on generated prose: deterministic, no LLM call, and it fails for the right reason.
#
#   includes - `value` appears in a retrieved chunk's title or text
#   first    - `value` appears in the top-ranked retrieved chunk

- id: opleidingsbudget
  question: Hoeveel opleidingsbudget heb ik per jaar?
  check: {type: includes, value: "EUR 2000"}
  steps: {1: true, 2: true, 3: true, 4: true, 5: true, 6: true}

- id: xximo
  question: Hoe geef ik mijn kilometerstand door aan XXimo?
  check: {type: includes, value: "XXimo portaal"}
  steps: {1: false, 2: true, 3: true, 4: true, 5: true, 6: true}

- id: kubernetes-hulp
  question: Wie kan me helpen met Kubernetes?
  check: {type: first, value: "Dries Peeters"}
  steps: {1: false, 2: false, 3: true, 4: true, 5: true, 6: true}

- id: conferentie-lissabon
  question: Mag ik mijn opleidingsbudget gebruiken voor een conferentie in Lissabon?
  check: {type: includes, value: "congressen en vakbeurzen"}
  steps: {1: false, 2: false, 3: false, 4: true, 5: true, 6: true}

- id: creditsaldo
  question: Hoeveel credits heeft Dries Peeters nog?
  check: {type: includes, value: "Huidig saldo"}
  steps: {1: false, 2: false, 3: false, 4: false, 5: false, 6: true}
```

- [ ] **Step 2: Write the failing test**

`app/tests/test_scoreboard.py`:

```python
"""The session's thesis as an assertion.

Marked slow: it needs the real embedding and reranker models and a built index.
Run it before writing slides, and again the morning of the talk.
"""

from pathlib import Path

import pytest
import yaml

from rag.app import build_engine
from rag.models import WIZARD_STEPS

APP = Path(__file__).resolve().parents[1]
QUESTIONS = yaml.safe_load((APP / "questions.yaml").read_text(encoding="utf-8"))

pytestmark = pytest.mark.slow


@pytest.fixture(scope="module")
def engine():
    return build_engine(APP / "data" / "index", APP / "data" / "cache")


def _passes(check: dict, result) -> bool:
    value = check["value"].lower()
    if check["type"] == "first":
        top = result.used[0].chunk if result.used else None
        return bool(top) and value in f"{top.title} {top.text}".lower()
    return any(value in f"{s.chunk.title} {s.chunk.text}".lower() for s in result.used)


@pytest.mark.parametrize("spec", QUESTIONS, ids=[q["id"] for q in QUESTIONS])
@pytest.mark.parametrize("step", WIZARD_STEPS, ids=[f"step{s.number}" for s in WIZARD_STEPS])
def test_scoreboard(engine, spec, step):
    result = engine.run(spec["question"], step.config)
    expected = spec["steps"][step.number]
    actual = _passes(spec["check"], result)
    assert actual == expected, (
        f"{spec['id']} at step {step.number} ({step.name}): "
        f"expected {'pass' if expected else 'fail'}, got {'pass' if actual else 'fail'}"
    )
```

- [ ] **Step 3: Run the test to verify it fails**

Run: `cd app && uv run pytest tests/test_scoreboard.py -m slow -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'rag.app'`

- [ ] **Step 4: Write the wiring module**

`app/rag/app.py`:

```python
"""Assembles an Engine from artefacts on disk. Used by the server, the scripts and the tests."""

from __future__ import annotations

from pathlib import Path

from rag.embed import embed_query
from rag.index import Bm25Index, DenseIndex
from rag.llm import build_llm
from rag.pipeline import Engine
from rag.rerank import CrossEncoderReranker
from rag.store import load_artefacts

APP_DIR = Path(__file__).resolve().parents[1]
INDEX_DIR = APP_DIR / "data" / "index"
CACHE_DIR = APP_DIR / "data" / "cache"


def build_engine(index_dir: Path = INDEX_DIR, cache_dir: Path = CACHE_DIR) -> Engine:
    chunks, vectors, _ = load_artefacts(index_dir)
    return Engine(
        dense=DenseIndex(chunks, vectors),
        bm25=Bm25Index(chunks),
        reranker=CrossEncoderReranker(),
        llm=build_llm(cache_dir),
        embed_query=embed_query,
    )


def load_projection(index_dir: Path = INDEX_DIR):
    chunks, _, projection = load_artefacts(index_dir)
    return chunks, projection
```

- [ ] **Step 5: Run the scoreboard and reconcile it with reality**

Run: `cd app && uv run pytest tests/test_scoreboard.py -m slow -v`

Expected: 30 tests. **Some will fail**, and that is information, not a defect. Work through failures in this order:

1. If a question passes at a step where it should fail, the question is too easy against this corpus. Sharpen it, or make the corpus more realistic — do not weaken the check.
2. If a question fails at the step that should fix it, the technique is not doing what the notes claim here. Check `result.candidates` ranks first: if the right chunk is in `candidates` but not `used`, the problem is `top_n`; if it is absent from `candidates`, the problem is retrieval.
3. Only once the sample corpus produces a green scoreboard, move on. Adjust `questions.yaml` last, and record any change in the spec's Risks section.

- [ ] **Step 6: Commit**

```bash
git add app/questions.yaml app/rag/app.py app/tests/test_scoreboard.py
git commit -m "Add the scoreboard test asserting all five questions per wizard step"
```

---

### Task 14: The HTTP API

**Files:**
- Create: `app/web/__init__.py`
- Create: `app/web/server.py`
- Test: `app/tests/test_server.py`

- [ ] **Step 1: Write the failing tests**

`app/tests/test_server.py`:

```python
import numpy as np
import pytest
from fastapi.testclient import TestClient

from rag.index import Bm25Index, DenseIndex
from rag.models import Chunk
from rag.pipeline import Engine
from web.server import create_app


class StubLLM:
    def complete(self, system: str, prompt: str, **kwargs) -> str:
        return "An answer [1]."


class NullReranker:
    def score(self, query: str, texts: list[str]) -> list[float]:
        return [0.0] * len(texts)


@pytest.fixture
def client():
    chunks = [
        Chunk(id="a", text="AZ-204 azure", source="s", source_type="cv", title="Bram", location="l"),
        Chunk(id="b", text="kubernetes", source="s", source_type="cv", title="Dries", location="l"),
    ]
    vectors = np.array([[1.0, 0.0], [0.0, 1.0]], dtype=np.float32)
    engine = Engine(
        dense=DenseIndex(chunks, vectors),
        bm25=Bm25Index(chunks),
        reranker=NullReranker(),
        llm=StubLLM(),
        embed_query=lambda _: np.array([1.0, 0.0], dtype=np.float32),
    )
    projection = np.array([[0.1, 0.2], [0.3, 0.4]], dtype=np.float32)
    return TestClient(create_app(engine, chunks, projection))


def test_steps_endpoint_returns_the_five_wizard_steps(client):
    steps = client.get("/api/steps").json()
    assert [s["number"] for s in steps] == [1, 2, 3, 4, 5]
    assert steps[1]["config"]["bm25"] is True


def test_questions_endpoint_returns_the_five_questions(client):
    questions = client.get("/api/questions").json()
    assert len(questions) == 5
    assert all("question" in q for q in questions)


def test_ask_returns_answer_used_and_candidates(client):
    body = client.post("/api/ask", json={"question": "AZ-204", "step": 1}).json()
    assert body["answer"] == "An answer [1]."
    assert body["used"]
    assert "ranks" in body["used"][0]


def test_ask_accepts_a_raw_config_from_the_advanced_panel(client):
    body = client.post(
        "/api/ask",
        json={"question": "AZ-204", "config": {"dense": True, "bm25": True, "top_n": 1}},
    ).json()
    assert len(body["used"]) == 1


def test_map_returns_a_point_per_chunk(client):
    points = client.get("/api/map").json()
    assert len(points) == 2
    assert {"x", "y", "id", "title", "source_type", "text"} <= set(points[0])


def test_map_query_returns_the_query_point_and_neighbours(client):
    body = client.post("/api/map/query", json={"question": "AZ-204", "k": 1}).json()
    assert "x" in body and "y" in body
    assert body["neighbours"] == ["a"]


def test_index_page_is_served(client):
    assert client.get("/").status_code == 200
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `cd app && uv run pytest tests/test_server.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'web.server'`

- [ ] **Step 3: Write the implementation**

```bash
touch app/web/__init__.py
```

`app/web/server.py`:

```python
from __future__ import annotations

from dataclasses import asdict
from pathlib import Path

import numpy as np
import yaml
from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel

from rag.llm import NoAnswerAvailable
from rag.models import Chunk, Config, Result, WIZARD_STEPS
from rag.pipeline import Engine

STATIC = Path(__file__).resolve().parent / "static"
QUESTIONS_FILE = Path(__file__).resolve().parents[1] / "questions.yaml"


class AskRequest(BaseModel):
    question: str
    step: int | None = None
    config: dict | None = None


class MapQuery(BaseModel):
    question: str
    k: int = 5


def _config_for(request: AskRequest) -> Config:
    if request.config is not None:
        return Config(**request.config)
    if request.step is not None:
        return WIZARD_STEPS[request.step - 1].config
    return Config()


def _scored_json(scored) -> dict:
    return {
        "id": scored.chunk.id,
        "title": scored.chunk.title,
        "location": scored.chunk.location,
        "source_type": scored.chunk.source_type,
        "text": scored.chunk.text,
        "score": scored.score,
        "ranks": scored.ranks,
    }


def _result_json(result: Result) -> dict:
    return {
        "question": result.question,
        "rewritten": result.rewritten,
        "answer": result.answer,
        "citations": [asdict(c) for c in result.citations],
        "used": [_scored_json(s) for s in result.used],
        "candidates": [_scored_json(s) for s in result.candidates[:20]],
    }


def create_app(engine: Engine, chunks: list[Chunk], projection: np.ndarray) -> FastAPI:
    app = FastAPI(title="RAG demo")

    @app.get("/")
    def index() -> FileResponse:
        return FileResponse(STATIC / "index.html")

    @app.get("/api/steps")
    def steps() -> list[dict]:
        return [
            {
                "number": s.number,
                "name": s.name,
                "blurb": s.blurb,
                "config": asdict(s.config),
            }
            for s in WIZARD_STEPS
        ]

    @app.get("/api/questions")
    def questions() -> list[dict]:
        specs = yaml.safe_load(QUESTIONS_FILE.read_text(encoding="utf-8"))
        return [
            {"id": s["id"], "question": s["question"], "steps": s["steps"]} for s in specs
        ]

    @app.post("/api/ask")
    def ask(request: AskRequest) -> dict:
        try:
            result = engine.run(request.question, _config_for(request))
        except NoAnswerAvailable as exc:
            return {"error": str(exc)}
        return _result_json(result)

    @app.get("/api/map")
    def map_points() -> list[dict]:
        return [
            {
                "id": chunk.id,
                "x": float(point[0]),
                "y": float(point[1]),
                "title": chunk.title,
                "source_type": chunk.source_type,
                "text": chunk.text[:400],
            }
            for chunk, point in zip(chunks, projection)
        ]

    @app.post("/api/map/query")
    def map_query(request: MapQuery) -> dict:
        vector = engine.embed_query(request.question)
        hits = engine.dense.search(vector, request.k)
        neighbour_ids = [chunk.id for chunk, _ in hits]
        # Place the query where its neighbours are: the projection is fitted on the
        # corpus and cannot transform an unseen point in a way the room would trust.
        index = {c.id: i for i, c in enumerate(chunks)}
        points = np.array([projection[index[cid]] for cid in neighbour_ids])
        centre = points.mean(axis=0)
        return {
            "x": float(centre[0]),
            "y": float(centre[1]),
            "neighbours": neighbour_ids,
        }

    return app


def build() -> FastAPI:
    from rag.app import build_engine, load_projection

    chunks, projection = load_projection()
    return create_app(build_engine(), chunks, projection)
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `cd app && uv run pytest tests/test_server.py -v`
Expected: 7 passed. The `/` test needs `web/static/index.html` to exist — create a placeholder first if it does not:

```bash
mkdir -p app/web/static && echo "<h1>RAG demo</h1>" > app/web/static/index.html
```

- [ ] **Step 5: Commit**

```bash
git add app/web/__init__.py app/web/server.py app/web/static/index.html app/tests/test_server.py
git commit -m "Add the HTTP API for the wizard and the embedding map"
```

---

### Task 15: The UI

**Files:**
- Modify: `app/web/static/index.html` (replaces the placeholder in full)

- [ ] **Step 1: Write the page**

`app/web/static/index.html`:

```html
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>RAG &amp; Embeddings</title>
<script src="https://cdn.plot.ly/plotly-2.35.2.min.js" charset="utf-8"></script>
<script defer src="https://cdn.jsdelivr.net/npm/alpinejs@3.14.1/dist/cdn.min.js"></script>
<style>
  :root {
    --bg: #12141a; --panel: #1a1d25; --line: #2c313d;
    --ink: #e8eaf0; --dim: #8d94a5; --accent: #6ea8fe;
    --pass: #4ade80; --fail: #f87171;
  }
  * { box-sizing: border-box; }
  body {
    margin: 0; background: var(--bg); color: var(--ink);
    font: 16px/1.55 ui-sans-serif, system-ui, -apple-system, "Segoe UI", sans-serif;
  }
  header {
    display: flex; align-items: center; gap: 1.5rem;
    padding: 1rem 1.5rem; border-bottom: 1px solid var(--line);
  }
  header h1 { font-size: 1.1rem; margin: 0; font-weight: 600; letter-spacing: .01em; }
  .steps { display: flex; gap: .5rem; margin-left: auto; }
  .steps button {
    background: var(--panel); color: var(--dim); border: 1px solid var(--line);
    border-radius: 6px; padding: .45rem .9rem; font: inherit; font-size: .85rem;
    cursor: pointer;
  }
  .steps button.on { background: var(--accent); border-color: var(--accent); color: #0b0d12; font-weight: 600; }
  .steps button.done { color: var(--ink); border-color: var(--accent); }
  main { display: grid; grid-template-columns: 300px 1fr; gap: 1.5rem; padding: 1.5rem; }
  .panel { background: var(--panel); border: 1px solid var(--line); border-radius: 10px; padding: 1.1rem; }
  h2 { font-size: .8rem; text-transform: uppercase; letter-spacing: .08em; color: var(--dim); margin: 0 0 .8rem; }
  .scoreboard li { list-style: none; display: flex; gap: .55rem; padding: .3rem 0; font-size: .9rem; }
  .scoreboard ul { margin: 0; padding: 0; }
  .scoreboard .v { width: 1.2rem; }
  .pass { color: var(--pass); } .fail { color: var(--fail); }
  .scoreboard button {
    background: none; border: none; color: inherit; font: inherit; text-align: left;
    cursor: pointer; padding: 0; flex: 1;
  }
  .ask { display: flex; gap: .6rem; margin-bottom: 1.2rem; }
  .ask input {
    flex: 1; background: var(--panel); border: 1px solid var(--line); border-radius: 8px;
    padding: .7rem .9rem; color: var(--ink); font: inherit;
  }
  .ask button {
    background: var(--accent); color: #0b0d12; border: 0; border-radius: 8px;
    padding: .7rem 1.4rem; font: inherit; font-weight: 600; cursor: pointer;
  }
  .blurb { color: var(--dim); font-size: .9rem; margin: 0 0 1rem; }
  .rewritten { border-left: 3px solid var(--accent); padding-left: .8rem; margin-bottom: 1rem; font-size: .9rem; }
  .answer { white-space: pre-wrap; margin-bottom: 1.2rem; }
  .chunk { border-top: 1px solid var(--line); padding: .8rem 0; font-size: .88rem; }
  .chunk:first-of-type { border-top: 0; }
  .chunk h3 { margin: 0 0 .25rem; font-size: .92rem; }
  .chunk .meta { color: var(--dim); font-size: .78rem; margin-bottom: .4rem; }
  .chunk .body { color: #c3c8d4; }
  .rank { display: inline-block; background: #232733; border-radius: 4px; padding: .05rem .4rem; margin-right: .3rem; font-size: .72rem; }
  .rank.up { background: #16351f; color: var(--pass); }
  details.advanced { margin-top: 1.5rem; font-size: .85rem; color: var(--dim); }
  details.advanced label { margin-right: 1rem; }
  #map { height: 620px; }
  .error { color: var(--fail); }
</style>
</head>
<body x-data="demo()" x-init="init()">

<header>
  <h1>RAG &amp; Embeddings</h1>
  <nav class="steps">
    <button @click="goto(0)" :class="step === 0 ? 'on' : ''">0 · Map</button>
    <template x-for="s in steps" :key="s.number">
      <button @click="goto(s.number)"
              :class="step === s.number ? 'on' : (step > s.number ? 'done' : '')"
              x-text="s.number + ' · ' + s.name"></button>
    </template>
  </nav>
</header>

<main x-show="step === 0" style="grid-template-columns: 1fr">
  <section class="panel">
    <h2>The map of meaning</h2>
    <form class="ask" @submit.prevent="plotQuery()">
      <input x-model="mapQuestion" placeholder="Drop a question on the map…">
      <button type="submit">Find nearest</button>
    </form>
    <div id="map"></div>
  </section>
</main>

<main x-show="step > 0">
  <aside class="panel scoreboard">
    <h2>Scoreboard</h2>
    <ul>
      <template x-for="q in questions" :key="q.id">
        <li>
          <span class="v" :class="q.steps[step] ? 'pass' : 'fail'"
                x-text="q.steps[step] ? '✅' : '❌'"></span>
          <button @click="ask(q.question)" x-text="q.question"></button>
        </li>
      </template>
    </ul>
    <details class="advanced">
      <summary>Advanced</summary>
      <template x-for="flag in ['dense','bm25','rerank','rewrite','citations']" :key="flag">
        <label>
          <input type="checkbox" :checked="config()[flag]" @change="override(flag, $event.target.checked)">
          <span x-text="flag"></span>
        </label>
      </template>
    </details>
  </aside>

  <section class="panel">
    <p class="blurb" x-text="current().blurb"></p>
    <form class="ask" @submit.prevent="ask(question)">
      <input x-model="question" placeholder="Ask something…">
      <button type="submit" x-text="loading ? '…' : 'Ask'"></button>
    </form>

    <p class="error" x-show="error" x-text="error"></p>

    <template x-if="result">
      <div>
        <p class="rewritten" x-show="result.rewritten">
          Searched for: <em x-text="result.rewritten"></em>
        </p>
        <div class="answer" x-text="result.answer"></div>

        <h2>Retrieved</h2>
        <template x-for="c in result.used" :key="c.id">
          <div class="chunk">
            <h3 x-text="c.title"></h3>
            <div class="meta">
              <template x-for="[stage, rank] in Object.entries(c.ranks)" :key="stage">
                <span class="rank" :class="rankImproved(c, stage) ? 'up' : ''"
                      x-text="stage + ' #' + rank"></span>
              </template>
              <span x-text="c.location"></span>
            </div>
            <div class="body" x-text="c.text.slice(0, 320)"></div>
          </div>
        </template>
      </div>
    </template>
  </section>
</main>

<script>
function demo() {
  return {
    step: 0, steps: [], questions: [], question: '', mapQuestion: '',
    result: null, loading: false, error: '', overrides: {}, points: [],

    async init() {
      this.steps = await (await fetch('/api/steps')).json();
      this.questions = await (await fetch('/api/questions')).json();
      this.points = await (await fetch('/api/map')).json();
      this.drawMap();
    },

    current() { return this.steps[this.step - 1] || { blurb: '', config: {} }; },
    config() { return { ...this.current().config, ...this.overrides }; },

    goto(n) {
      this.step = n;
      this.overrides = {};
      this.result = null;
      if (n === 0) this.$nextTick(() => this.drawMap());
    },

    override(flag, value) {
      this.overrides[flag] = value;
      if (this.question) this.ask(this.question);
    },

    rankImproved(chunk, stage) {
      const ranks = Object.entries(chunk.ranks);
      const i = ranks.findIndex(([s]) => s === stage);
      return i > 0 && ranks[i][1] < ranks[i - 1][1];
    },

    async ask(question) {
      this.question = question;
      this.loading = true;
      this.error = '';
      const body = { question, config: this.config() };
      const response = await (await fetch('/api/ask', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      })).json();
      this.loading = false;
      if (response.error) { this.error = response.error; this.result = null; }
      else { this.result = response; }
    },

    traces(highlight) {
      const types = [...new Set(this.points.map(p => p.source_type))];
      const colours = { policy: '#6ea8fe', cv: '#4ade80', bamboo: '#fbbf24', project: '#f472b6' };
      return types.map(type => {
        const pts = this.points.filter(p => p.source_type === type);
        return {
          x: pts.map(p => p.x), y: pts.map(p => p.y),
          text: pts.map(p => p.title + '<br>' + p.text.slice(0, 160)),
          hoverinfo: 'text', mode: 'markers', type: 'scatter', name: type,
          marker: {
            size: pts.map(p => highlight.includes(p.id) ? 16 : 8),
            color: colours[type] || '#8d94a5',
            line: { width: pts.map(p => highlight.includes(p.id) ? 2 : 0), color: '#fff' },
          },
        };
      });
    },

    layout() {
      return {
        paper_bgcolor: '#1a1d25', plot_bgcolor: '#1a1d25',
        font: { color: '#e8eaf0' }, margin: { t: 10, r: 10, b: 30, l: 30 },
        xaxis: { gridcolor: '#2c313d', zeroline: false },
        yaxis: { gridcolor: '#2c313d', zeroline: false },
        legend: { orientation: 'h' },
      };
    },

    drawMap(highlight = [], query = null) {
      const traces = this.traces(highlight);
      if (query) {
        traces.push({
          x: [query.x], y: [query.y], mode: 'markers+text', type: 'scatter',
          name: 'your question', text: ['?'], textposition: 'top center',
          marker: { size: 20, color: '#f87171', symbol: 'x' },
        });
      }
      Plotly.newPlot('map', traces, this.layout(), { displayModeBar: false });
    },

    async plotQuery() {
      const response = await (await fetch('/api/map/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: this.mapQuestion, k: 5 }),
      })).json();
      this.drawMap(response.neighbours, response);
    },
  };
}
</script>
</body>
</html>
```

- [ ] **Step 2: Run the server and check it by hand**

```bash
cd app
uv run uvicorn --factory web.server:build --reload --port 8000
```

Open `http://localhost:8000`. Confirm: the map renders with coloured clusters per source type; "Find nearest" places a red ✕ and enlarges five points; steps 1–5 switch; clicking a scoreboard question fills the box and returns an answer; rank badges appear on retrieved chunks.

- [ ] **Step 3: Run the full test suite**

Run: `cd app && uv run pytest -v`
Expected: all non-slow tests pass.

- [ ] **Step 4: Commit**

```bash
git add app/web/static/index.html
git commit -m "Add the wizard UI and embedding map page"
```

---

### Task 16: Cache warming and the README

**Files:**
- Create: `app/scripts/warm_cache.py`
- Create: `app/README.md`

- [ ] **Step 1: Write the warming script**

`app/scripts/warm_cache.py`:

```python
"""Fill the answer cache before the talk.

Every question at every wizard step. After this runs, the scripted demo makes no
network calls at all, which is also what stops a 'failing' question from accidentally
succeeding live.
"""

from __future__ import annotations

import sys
from pathlib import Path

APP = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(APP))

import yaml  # noqa: E402

from rag.app import build_engine  # noqa: E402
from rag.models import WIZARD_STEPS  # noqa: E402


def main() -> None:
    engine = build_engine()
    specs = yaml.safe_load((APP / "questions.yaml").read_text(encoding="utf-8"))
    for spec in specs:
        for step in WIZARD_STEPS:
            engine.run(spec["question"], step.config)
            print(f"  {spec['id']} · step {step.number} {step.name}")
    print(f"\nWarmed {len(specs) * len(WIZARD_STEPS)} entries.")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Run it**

```bash
cd app
uv run python scripts/warm_cache.py
```

Expected: 30 lines and a final count. Requires a working `ant auth login` profile.

- [ ] **Step 3: Write the README**

`app/README.md`:

````markdown
# RAG demo app

The live demo for the [RAG & Embeddings session](../notes/Session-Outline.md). Five
questions, a five-step wizard, four of them go green.

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

`build_index.py` prefers `data/raw/` over `sample/` when it exists. Nothing under
`data/` is ever committed: chunks are plaintext CV and HR text, embeddings can be
inverted back to approximate text, and cached answers quote both.

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

## Commands

| Command | Does |
| --- | --- |
| `uv run pytest` | Unit tests, no models, no network |
| `uv run pytest -m slow` | The scoreboard, against the built index |
| `uv run python scripts/build_index.py` | Ingest, embed, project |
| `uv run python scripts/warm_cache.py` | Fill the answer cache |
| `uv run uvicorn --factory web.server:build --port 8000` | Serve the app |
````

- [ ] **Step 4: Commit**

```bash
git add app/scripts/warm_cache.py app/README.md
git commit -m "Add cache warming script and app README"
```

---

## Done when

- `uv run pytest` is green with no network access.
- `uv run pytest -m slow` produces a green 30-assertion scoreboard, or the disagreements
  are understood and `questions.yaml` and the spec's Risks section are updated to match.
- The app runs from a clean clone against `sample/` with no credential, once the index
  is built.
- Every one of the five questions can be clicked through all six wizard steps with no
  network call.
