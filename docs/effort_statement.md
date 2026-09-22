# Declared Effort Statement

## Approximate time spent

| Activity | Hours |
|----------|-------|
| Problem definition and spec writing | 1.5 h |
| Synthetic data creation (10 YAML + 4 notes) | 2.0 h |
| Ingestion pipeline (ingest.py) | 1.5 h |
| Query pipeline (query.py) | 1.0 h |
| Streamlit UI (app.py) | 1.0 h |
| Context engineering (CLAUDE.md + before/after runs) | 1.0 h |
| AI output review | 1.0 h |
| Failure analysis (finding + documenting 5 failures) | 1.5 h |
| Improvement implementation + measurement | 0.5 h |
| Documentation (pitch, provenance, effort) | 0.5 h |
| **Total** | **11.5 h** |

## What I cut

**Cut: Live OpenAPI spec scraping.** The original plan included an n8n workflow that would
poll a mock API gateway for spec changes and trigger re-ingestion automatically. This was cut
because it added complexity (n8n setup, webhook configuration) without adding to the core
RAG demonstration. The ingestion pipeline is designed to be re-run manually when specs change,
which is sufficient for the prototype scope.

**Cut: Per-endpoint test assertions.** I planned to write a test for each of the 38 endpoints,
asserting that a natural-language query about each endpoint returns it as a top-3 result.
This was cut because it requires a running ChromaDB instance in CI and the value is low for
a local prototype. The 5 failure-analysis queries serve as the manual test suite.

**Cut: Docker/containerisation.** A `docker-compose.yml` would have made setup easier but
added 2+ hours of work for packaging something that runs fine locally with one pip install.

**Cut: Conversation history in the query pipeline.** The current implementation treats each
question as independent. A multi-turn conversation mode (where the assistant remembers previous
context) was considered but cut — it adds complexity to the LLM call and the primary use case
(endpoint lookup) is stateless.

## What I would do with another 4 hours

1. Add a minimum similarity score threshold (fix for Failure 5 — subscription hallucination)
2. Tag endpoint chunks with synonyms to fix the "capture vs charge" vocabulary gap (Failure 4)
3. Add a dedicated full-flow chunk for the order checkout sequence (Failure 3)
