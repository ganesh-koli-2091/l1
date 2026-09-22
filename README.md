# API Documentation Assistant

**L1_Case05_Open_Choice_Prototype** — Perficient Global AI-First Academy

A RAG-based assistant that answers plain-English questions about a microservices API
and always cites the source endpoint. Built on ChromaDB + sentence-transformers + Claude.

---

## Setup (5 minutes)

### Prerequisites
- Python 3.10+
- An Anthropic API key ([get one here](https://console.anthropic.com))

### Steps

```bash
# 1. Clone / navigate to the project
cd api-docs-assistant

# 2. Create and activate a virtual environment
python -m venv .venv

# Windows
.venv\Scripts\activate

# Mac/Linux
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set your API key
copy .env.example .env
# Open .env and replace: ANTHROPIC_API_KEY=your_anthropic_api_key_here

# 5. Ingest the documentation (one-time, ~30-60 seconds)
python src/ingest.py

# 6. Launch the app
streamlit run src/app.py
```

The app opens at `http://localhost:8501`.

---

## Re-ingesting after data changes

```bash
python src/ingest.py --reset
```

---

## Project structure

```
api-docs-assistant/
├── spec.md                      ← Specification (committed before code)
├── plan.md                      ← Implementation plan
├── tasks.md                     ← Task breakdown
├── CLAUDE.md                    ← Context artifact (system prompt for LLM)
├── requirements.txt
├── .env.example
│
├── data/
│   ├── openapi/                 ← 10 synthetic OpenAPI 3.0 YAML specs
│   └── notes/                   ← 4 architecture/pattern notes in Markdown
│
├── src/
│   ├── config.py                ← Paths, model names, env vars
│   ├── ingest.py                ← Load → Chunk → Embed → Store
│   ├── query.py                 ← Embed → Retrieve → LLM → Return
│   └── app.py                   ← Streamlit chat UI
│
├── evidence/
│   ├── before_context_output.md ← 3 queries without CLAUDE.md
│   └── after_context_output.md  ← Same 3 queries with CLAUDE.md
│
└── docs/
    ├── data_provenance.md
    ├── ai_output_review.md
    ├── failure_analysis.md
    ├── improvement_log.md
    ├── pitch_slide.md
    └── effort_statement.md
```

---

## What the system covers

- **10 services:** Order, Customer, Product, Payment, Inventory, Notification, Auth, Shipping, Cart, Analytics
- **~38 endpoints** across all services
- **4 notes:** architecture overview, common patterns, authentication guide, error handling

---

## Known limitations (see docs/failure_analysis.md for detail)

1. Batch operation questions return the wrong answer (no batch endpoints in corpus)
2. Rate-limit queries sometimes miss the notes doc (retrieval gap)
3. Full checkout-flow questions miss the inventory reservation step
4. "Capture" as a synonym for payment charge sometimes retrieves inventory endpoints
5. Non-existent features (e.g. subscriptions) may produce hallucinated answers

---

## Submission checklist coverage

| Requirement | File |
|-------------|------|
| Problem statement | spec.md |
| Data provenance | docs/data_provenance.md |
| Spec → Plan → Tasks before code | spec.md, plan.md, tasks.md |
| Working prototype | src/app.py + src/ingest.py |
| Context artifact + before/after | CLAUDE.md + evidence/ |
| RAG pipeline (load→chunk→embed→store→query) | src/ingest.py + src/query.py |
| AI output review | docs/ai_output_review.md |
| Failure analysis | docs/failure_analysis.md |
| One measured improvement | docs/improvement_log.md |
| Pitch slide | docs/pitch_slide.md |
| Declared effort | docs/effort_statement.md |
