"""
Retrieval-only diagnostic — prints the top N chunks for each failure input
without making any LLM call. Runs without a Portkey or Anthropic key.

Usage:
    python src/retrieve_only.py

This lets reviewers verify what the retriever surfaces for the five documented
failure cases in docs/failure_analysis.md without needing gateway access.
"""

import sys
from pathlib import Path

import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

sys.path.insert(0, str(Path(__file__).parent))
from config import CHROMA_DIR, COLLECTION_NAME, EMBEDDING_MODEL, N_RESULTS

FAILURE_INPUTS = [
    "How do I create multiple orders at once?",
    "What is the rate limit for calling the payment endpoint?",
    "Walk me through the complete checkout flow — every endpoint I need to call in order.",
    "How do I call the payment capture API?",
    "Which endpoint handles subscription management?",
]


def main() -> None:
    ef = SentenceTransformerEmbeddingFunction(model_name=EMBEDDING_MODEL)
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    existing = [c.name for c in client.list_collections()]
    if COLLECTION_NAME not in existing:
        print(f"Collection '{COLLECTION_NAME}' not found. Run: python src/ingest.py")
        sys.exit(1)

    collection = client.get_collection(name=COLLECTION_NAME, embedding_function=ef)

    for i, question in enumerate(FAILURE_INPUTS, 1):
        print(f"\n{'='*70}")
        print(f"Failure {i}: {question}")
        print(f"{'='*70}")

        results = collection.query(
            query_texts=[question],
            n_results=N_RESULTS,
            include=["documents", "metadatas", "distances"],
        )

        docs = results["documents"][0]
        metas = results["metadatas"][0]
        distances = results["distances"][0]

        for rank, (doc, meta, dist) in enumerate(zip(docs, metas, distances), 1):
            score = round(1 - dist, 3)
            source = meta.get("source", "?")
            chunk_type = meta.get("type", "?")
            if chunk_type == "endpoint":
                label = f"{meta.get('method', '')} {meta.get('path', '')} — {source}"
            else:
                label = f"{meta.get('title', source)} — {source}"
            print(f"  [{rank}] score={score:.3f}  {label}")
            print(f"       {doc[:120].replace(chr(10), ' ')}...")


if __name__ == "__main__":
    main()
