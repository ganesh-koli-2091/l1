# Specification — Internal API Documentation Assistant

**Case ID:** L1_Case05_Open_Choice_Prototype
**Committed:** before any implementation code

---

## Problem Statement

ShopCo's backend engineering team has grown from 3 to 18 developers over the past year.
The microservices platform now spans 10 services with over 80 endpoints. Junior developers
spend 30–45 minutes per task searching through scattered Confluence pages, Swagger UIs on
different ports, and Slack DMs just to find which endpoint to call and what parameters it needs.

**Domain:** Technology consulting / internal developer tooling
**User:** Junior to mid-level backend developer onboarding to a microservices platform
**Problem:** No single place to ask "which endpoint handles X?" and get a cited, correct answer
**Definition of success:** A developer can ask a plain-English question about the API and receive,
in under 10 seconds, the exact endpoint path, HTTP method, required parameters, and
authentication requirements — with the source document cited.

---

## Scope

### In scope
- RAG pipeline over synthetic OpenAPI YAML specs (10 services, ~80 endpoints)
- RAG pipeline over architecture notes in Markdown (4 documents)
- Streamlit chat UI for querying
- CLAUDE.md context artifact with before/after evidence
- AI output review, failure analysis, measured improvement

### Out of scope
- Live Swagger UI scraping (data is synthetic)
- Multi-tenant access control
- Fine-tuning or custom embedding model
- Production deployment / Docker

---

## Functional Requirements

| ID  | Requirement |
|-----|-------------|
| FR1 | System MUST answer questions about which endpoint to call for a given task |
| FR2 | Every answer MUST cite the source file, HTTP method, and path |
| FR3 | System MUST list required parameters in its answer |
| FR4 | System MUST flag authentication requirements |
| FR5 | System MUST suggest related endpoints when the question implies a workflow |
| FR6 | System MUST say so clearly when no matching endpoint is found |

---

## Non-Functional Requirements

| ID   | Requirement |
|------|-------------|
| NFR1 | Query latency under 10 seconds (including LLM call) |
| NFR2 | Runs locally on a developer laptop with no cloud infrastructure except the LLM API |
| NFR3 | Ingest pipeline completes in under 60 seconds for the full corpus |
| NFR4 | No PII in the dataset — all data is synthetic |

---

## Architecture Decision: RAG vs n8n Automation

**Chosen: RAG Pipeline**

Reason: The core problem is retrieval — finding the right endpoint from a large, static corpus.
RAG is the natural fit: the documents don't change frequently, and the user needs cited answers
from specific source documents, not a recurring automated workflow.

n8n automation would be the right choice if the problem were "notify me when the API changes"
or "generate a weekly digest of new endpoints" — both of which are monitoring/workflow problems.
The problem here is point-in-time retrieval by a human, which is a RAG problem.

---

## Tech Stack

| Component       | Choice                        | Rejected alternative |
|-----------------|-------------------------------|----------------------|
| Vector store    | ChromaDB (local, file-based)  | Pinecone (requires cloud account) |
| Embeddings      | sentence-transformers all-MiniLM-L6-v2 | OpenAI text-embedding-3-small (costs money per ingest) |
| LLM             | Anthropic Claude claude-opus-4-5 | GPT-4o (OpenAI; team has Anthropic access) |
| UI              | Streamlit                     | React (too much boilerplate for a prototype) |
| Data format     | OpenAPI 3.0 YAML + Markdown   | JSON API specs (less human-readable) |
