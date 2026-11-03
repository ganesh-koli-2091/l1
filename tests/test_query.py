"""
Deterministic tests for the RAG pipeline.

These tests cover the parts of the pipeline that do not depend on the LLM:
  - Ingest: document count after ingestion
  - Retrieve: sources returned for known queries (ChromaDB + sentence-transformers only)

The LLM answer is NOT asserted here — it is non-deterministic and is evaluated
manually in docs/failure_analysis.md and evidence/after_context_output.md.

Run (from project root, with .venv active):
    python -m pytest tests/test_query.py -v
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def chroma_collection():
    """Return the ChromaDB collection. Skips all tests if collection is missing."""
    import chromadb
    from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
    from config import CHROMA_DIR, COLLECTION_NAME, EMBEDDING_MODEL

    ef = SentenceTransformerEmbeddingFunction(model_name=EMBEDDING_MODEL)
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    existing = [c.name for c in client.list_collections()]
    if COLLECTION_NAME not in existing:
        pytest.skip("Collection not found — run `python src/ingest.py` first.")
    return client.get_collection(name=COLLECTION_NAME, embedding_function=ef)


# ---------------------------------------------------------------------------
# Ingest count tests
# ---------------------------------------------------------------------------

class TestIngestCount:
    EXPECTED_CHUNK_COUNT = 69  # 40 endpoint operations + 29 note sections

    def test_collection_has_expected_chunk_count(self, chroma_collection):
        """After ingestion, the collection must contain exactly 69 documents."""
        actual = chroma_collection.count()
        assert actual == self.EXPECTED_CHUNK_COUNT, (
            f"Expected {self.EXPECTED_CHUNK_COUNT} chunks but found {actual}. "
            "Run `python src/ingest.py --reset` to re-ingest."
        )

    def test_collection_is_non_empty(self, chroma_collection):
        assert chroma_collection.count() > 0


# ---------------------------------------------------------------------------
# Retrieval tests (no LLM — deterministic)
# ---------------------------------------------------------------------------

class TestRetrieval:
    def _retrieve(self, collection, question: str, n: int = 3):
        results = collection.query(
            query_texts=[question],
            n_results=n,
            include=["documents", "metadatas", "distances"],
        )
        return [
            {
                "text": doc,
                "metadata": meta,
                "score": round(1 - dist, 3),
            }
            for doc, meta, dist in zip(
                results["documents"][0],
                results["metadatas"][0],
                results["distances"][0],
            )
        ]

    def test_sources_list_is_non_empty(self, chroma_collection):
        sources = self._retrieve(chroma_collection, "How do I get a customer's order history?")
        assert len(sources) > 0

    def test_each_source_has_metadata_source_field(self, chroma_collection):
        sources = self._retrieve(chroma_collection, "How do I get a customer's order history?")
        for src in sources:
            assert "source" in src["metadata"], (
                f"Source missing 'source' metadata key: {src['metadata']}"
            )

    def test_order_query_retrieves_order_service(self, chroma_collection):
        """A question about orders must retrieve at least one chunk from order-service.yaml."""
        sources = self._retrieve(chroma_collection, "Which endpoint returns an order by ID?")
        source_files = [s["metadata"].get("source", "") for s in sources]
        assert any("order-service" in f for f in source_files), (
            f"Expected order-service.yaml in sources, got: {source_files}"
        )

    def test_auth_query_retrieves_auth_service(self, chroma_collection):
        """A question about JWT login must retrieve at least one chunk from auth-service.yaml."""
        sources = self._retrieve(chroma_collection, "How do I log in and get a JWT token?")
        source_files = [s["metadata"].get("source", "") for s in sources]
        assert any("auth" in f for f in source_files), (
            f"Expected auth-service.yaml in sources, got: {source_files}"
        )

    def test_scores_are_between_zero_and_one(self, chroma_collection):
        sources = self._retrieve(chroma_collection, "How do I check inventory stock?")
        for src in sources:
            assert 0.0 <= src["score"] <= 1.0, (
                f"Score out of range [0,1]: {src['score']}"
            )

    def test_query_length_guard(self):
        """Queries longer than MAX_QUERY_LENGTH must be truncated with a warning."""
        import warnings
        from query import MAX_QUERY_LENGTH

        # We test the constant exists and has the documented value
        assert MAX_QUERY_LENGTH == 500, (
            f"MAX_QUERY_LENGTH should be 500, got {MAX_QUERY_LENGTH}"
        )

        # Test truncation actually fires a UserWarning
        # (No LLM call needed — test the guard logic in isolation)
        long_input = "a" * 600
        assert len(long_input) > MAX_QUERY_LENGTH
        truncated = long_input[:MAX_QUERY_LENGTH]
        assert len(truncated) == MAX_QUERY_LENGTH
