# Implementation Plan — Internal API Documentation Assistant

**Committed:** after spec.md, before tasks.md and all implementation code

---

## Phase 1 — Data Creation

Generate 10 synthetic OpenAPI 3.0 YAML files covering a realistic e-commerce microservices
platform. Generate 4 Markdown architecture notes. All data is synthetic — no real company
data, no PII.

**Services to model:**
1. Order Service — order lifecycle (create, get, list, cancel, status)
2. Customer Service — customer profiles (register, get, update, list)
3. Product Service — product catalog (list, get, search)
4. Payment Service — payments (charge, status, refund)
5. Inventory Service — stock (check, reserve, update)
6. Notification Service — email/SMS (send, status)
7. Auth Service — JWT auth (login, logout, refresh, validate)
8. Shipping Service — shipments (create, track, rates)
9. Cart Service — shopping cart (add, remove, get, checkout)
10. Analytics Service — reporting (sales, top products, customer metrics)

**Notes files:**
- architecture-overview.md — service map, inter-service communication
- common-patterns.md — pagination, filtering, sorting conventions
- authentication-guide.md — JWT flow, token refresh, header format
- error-handling.md — standard error codes, retry guidance

---

## Phase 2 — Ingestion Pipeline

**Load:**
- Parse each OpenAPI YAML with PyYAML
- For each path + method combination, extract a structured text chunk
- Parse each Markdown file and split by H1/H2 headers

**Chunk strategy:**
- OpenAPI: one chunk per endpoint (path + method). Chunk contains: service name,
  method, path, summary, description, parameters, response schema, tags.
- Markdown: one chunk per section (split on # or ## header).
- Rationale: endpoint-level chunking keeps the retrieval unit coherent — fetching
  half an endpoint description is useless.

**Embed:**
- Use ChromaDB's built-in SentenceTransformerEmbeddingFunction with all-MiniLM-L6-v2
- Model downloads on first run (~80 MB), then cached locally

**Store:**
- ChromaDB PersistentClient at ./chroma_db
- Single collection "api_docs"
- Metadata stored per chunk: source filename, service name, method, path, type (endpoint|note)

---

## Phase 3 — Query Pipeline

1. Embed the user's question using the same sentence-transformer model
2. Retrieve top-5 most similar chunks from ChromaDB
3. Format retrieved chunks as context block
4. Call Anthropic Claude with system prompt (from CLAUDE.md) + context + user question
5. Return LLM answer + source list to UI

---

## Phase 4 — Streamlit UI

- Chat interface with message history
- Expandable "Source chunks" section per answer showing what was retrieved
- Warning banner if ChromaDB is not populated (ingest not run)
- Sidebar with example questions

---

## Phase 5 — Context Engineering Evidence

- Run 3 representative queries with a generic system prompt (no CLAUDE.md)
- Record outputs verbatim in evidence/before_context_output.md
- Write CLAUDE.md with structured answer format, citation rules, domain context
- Re-run same 3 queries with CLAUDE.md as system prompt
- Record outputs in evidence/after_context_output.md
- Write comparative analysis

---

## Phase 6 — Review, Failure Analysis, Improvement

- AI output review: check generated code/answers across 5 dimensions
- Failure analysis: 5 queries the system handles badly, with root causes
- Improvement: fix the most impactful failure, measure before/after

---

## Commit sequence (for assessor visibility)

```
commit 1: spec.md
commit 2: plan.md
commit 3: tasks.md
commit 4: data/ — all OpenAPI YAML and notes
commit 5: CLAUDE.md + requirements.txt + .env.example
commit 6: src/ — ingest.py, query.py, config.py, app.py
commit 7: evidence/ — before and after context outputs
commit 8: docs/ — review, failure analysis, improvement log, pitch, effort
```
