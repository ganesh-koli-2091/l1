# Task Breakdown — Internal API Documentation Assistant

**Committed:** after plan.md, before any implementation code

---

## T1 — Data Creation

- [x] T1.1: Create `data/openapi/order-service.yaml` — 5 endpoints
- [x] T1.2: Create `data/openapi/customer-service.yaml` — 4 endpoints
- [x] T1.3: Create `data/openapi/product-service.yaml` — 4 endpoints
- [x] T1.4: Create `data/openapi/payment-service.yaml` — 4 endpoints
- [x] T1.5: Create `data/openapi/inventory-service.yaml` — 3 endpoints
- [x] T1.6: Create `data/openapi/notification-service.yaml` — 3 endpoints
- [x] T1.7: Create `data/openapi/auth-service.yaml` — 4 endpoints
- [x] T1.8: Create `data/openapi/shipping-service.yaml` — 4 endpoints
- [x] T1.9: Create `data/openapi/cart-service.yaml` — 4 endpoints
- [x] T1.10: Create `data/openapi/analytics-service.yaml` — 3 endpoints
- [x] T1.11: Create `data/notes/architecture-overview.md`
- [x] T1.12: Create `data/notes/common-patterns.md`
- [x] T1.13: Create `data/notes/authentication-guide.md`
- [x] T1.14: Create `data/notes/error-handling.md`

## T2 — Project Config

- [x] T2.1: Create `requirements.txt`
- [x] T2.2: Create `.env.example`
- [x] T2.3: Create `src/config.py` — paths, model names, env vars

## T3 — Ingestion Pipeline

- [x] T3.1: Write OpenAPI YAML loader → extract one text chunk per endpoint
- [x] T3.2: Write Markdown loader → split by H1/H2 headers into sections
- [x] T3.3: Set up ChromaDB PersistentClient with SentenceTransformer embedding function
- [x] T3.4: Write `collection.add()` with document text + metadata
- [x] T3.5: Add `--reset` flag to force re-ingest
- [x] T3.6: Verify: run ingest, confirm correct document count

## T4 — Query Pipeline

- [x] T4.1: Write `APIDocsAssistant` class in `src/query.py`
- [x] T4.2: Implement `query()` — embed → retrieve → format context → LLM call
- [x] T4.3: Load CLAUDE.md as system prompt
- [x] T4.4: Return answer + source list with scores

## T5 — Streamlit UI

- [x] T5.1: Create `src/app.py` with chat interface and message history
- [x] T5.2: Add expandable source chunks panel per answer
- [x] T5.3: Add sidebar with 5 example questions
- [x] T5.4: Add warning if ChromaDB not populated
- [x] T5.5: Manual test: run 10 queries covering all 10 services

## T6 — Context Engineering Evidence

- [x] T6.1: Record 3 query outputs without CLAUDE.md → `evidence/before_context_output.md`
- [x] T6.2: Write `CLAUDE.md` with structured format + citation rules
- [x] T6.3: Record same 3 queries with CLAUDE.md → `evidence/after_context_output.md`

## T7 — Review and Analysis

- [x] T7.1: Write `docs/ai_output_review.md` — intent, tests, security, performance, maintainability
- [x] T7.2: Write `docs/failure_analysis.md` — 5 failure cases with specific inputs and root causes
- [x] T7.3: Fix the chunking failure (T3.1 improvement: include response schema in chunk text)
- [x] T7.4: Write `docs/improvement_log.md` — before/after with measured difference
- [x] T7.5: Write `docs/pitch_slide.md`
- [x] T7.6: Write `docs/effort_statement.md`
- [x] T7.7: Write `docs/data_provenance.md`

---

## Acceptance criteria

| Task | Done when |
|------|-----------|
| T3   | `python src/ingest.py` completes without error, prints "Ingested N documents" |
| T4   | `from src.query import APIDocsAssistant; a.query("get order by id")` returns cited answer |
| T5   | `streamlit run src/app.py` opens in browser, all 10 example queries return sourced answers |
| T6   | Before and after outputs show measurable citation improvement |
| T7   | At least 1 caught error in AI output review; at least 5 named failure inputs |
