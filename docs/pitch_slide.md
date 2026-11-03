# Pitch Slide — API Documentation Assistant

---

## The problem (one line)

Junior developers lose **30–45 minutes per task** searching across 10 Swagger UIs, scattered
Confluence pages, and Slack DMs to find one endpoint.

---

## What this is

An internal AI assistant that answers plain-English questions about the microservices API
and **always cites the source document, endpoint path, and required parameters**.

> Developer asks: *"How do I get a customer's order history?"*
> Assistant answers: *"Use GET /api/v1/orders with customerId as a query parameter.
> Requires Bearer token. Returns paginated order list. [Source: order-service.yaml, GET /orders]"*

---

## How it works

```
Developer question
       ↓
Embed query (sentence-transformers, runs locally)
       ↓
Search ChromaDB (10 OpenAPI specs + 4 architecture notes)
       ↓
Top 3 most relevant endpoint chunks retrieved
       ↓
GPT-4o-mini (via Portkey gateway) generates structured cited answer
       ↓
Answer + source panel shown in Streamlit UI
```

---

## What it covers today

- 10 microservices | 40 endpoints | 4 architecture notes | 69 indexed chunks
- Every answer cites the source file and endpoint
- Runs fully local except the LLM call (GPT-4o-mini via Portkey gateway)

---

## What it does not do (honest limits)

- Does not handle batch operation questions (no batch endpoints in corpus)
- Struggles with multi-step workflow questions (retrieval favours single endpoints)
- Rate limit per-endpoint questions sometimes miss the notes doc (see failure_analysis.md)
- No live sync with OpenAPI spec changes — requires re-ingestion when specs update

---

## Why this beats the current state

| Current state | With this assistant |
|---------------|---------------------|
| Dev opens 3 Swagger UIs | One chat interface |
| Searches Confluence for auth format | Auth requirement in every answer |
| DMs a teammate for parameter names | Parameters listed, typed, required/optional flagged |
| No traceability | Source document cited every time |

**Projected time saving:** 20–30 minutes per developer per day on the 18-person team = ~6 hours/day recovered.
