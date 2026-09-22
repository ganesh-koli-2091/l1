"""
Query pipeline: Embed → Retrieve → Format context → LLM call → Return cited answer
"""

import sys
from pathlib import Path

import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
from portkey_ai import Portkey

sys.path.insert(0, str(Path(__file__).parent))
from config import (
    CHROMA_DIR, CLAUDE_MD_PATH, EMBEDDING_MODEL,
    COLLECTION_NAME, LLM_MODEL, N_RESULTS, MAX_COMPLETION_TOKENS,
    PORTKEY_API_KEY, PORTKEY_BASE_URL,
    USE_DIRECT_ANTHROPIC, ANTHROPIC_API_KEY, DIRECT_LLM_MODEL,
    validate_config,
)


class APIDocsAssistant:
    def __init__(self) -> None:
        validate_config()

        ef = SentenceTransformerEmbeddingFunction(model_name=EMBEDDING_MODEL)
        client = chromadb.PersistentClient(path=str(CHROMA_DIR))

        existing = [c.name for c in client.list_collections()]
        if COLLECTION_NAME not in existing:
            raise RuntimeError(
                f"Collection '{COLLECTION_NAME}' not found. "
                "Run `python src/ingest.py` first."
            )

        self.collection = client.get_collection(
            name=COLLECTION_NAME,
            embedding_function=ef,
        )
        if USE_DIRECT_ANTHROPIC:
            # Fallback: call Anthropic directly (set USE_DIRECT_ANTHROPIC=true in .env)
            from anthropic import Anthropic
            self._anthropic_client = Anthropic(api_key=ANTHROPIC_API_KEY)
            self._use_direct = True
        else:
            self.llm = Portkey(base_url=PORTKEY_BASE_URL, api_key=PORTKEY_API_KEY)
            self._use_direct = False
        self.system_prompt = self._load_system_prompt()

    def _load_system_prompt(self) -> str:
        if CLAUDE_MD_PATH.exists():
            return CLAUDE_MD_PATH.read_text(encoding="utf-8")
        # Fallback: generic prompt used for before/after comparison
        return "You are a helpful API documentation assistant. Answer questions about the API."

    def query(self, question: str) -> dict:
        """
        Returns:
            answer (str): LLM response with citations
            sources (list[dict]): retrieved chunks with metadata and similarity scores
        """
        results = self.collection.query(
            query_texts=[question],
            n_results=N_RESULTS,
            include=["documents", "metadatas", "distances"],
        )

        docs = results["documents"][0]
        metadatas = results["metadatas"][0]
        distances = results["distances"][0]

        # Convert cosine distance to similarity score (0–1, higher = better)
        sources = [
            {
                "text": doc,
                "metadata": meta,
                "score": round(1 - dist, 3),
            }
            for doc, meta, dist in zip(docs, metadatas, distances)
        ]

        context = "\n\n---\n\n".join(docs)

        user_content = (
            "Use the following API documentation excerpts to answer the question.\n\n"
            f"DOCUMENTATION:\n{context}\n\n"
            f"QUESTION: {question}"
        )

        if self._use_direct:
            resp = self._anthropic_client.messages.create(
                model=DIRECT_LLM_MODEL,
                max_tokens=MAX_COMPLETION_TOKENS,
                system=self.system_prompt,
                messages=[{"role": "user", "content": user_content}],
            )
            answer = resp.content[0].text
        else:
            # GPT-5 is a reasoning model: must use max_completion_tokens, not max_tokens
            resp = self.llm.chat.completions.create(
                model=LLM_MODEL,
                max_completion_tokens=MAX_COMPLETION_TOKENS,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": user_content},
                ],
            )
            answer = resp.choices[0].message.content

        return {
            "question": question,
            "answer": answer,
            "sources": sources,
        }


if __name__ == "__main__":
    import json
    assistant = APIDocsAssistant()
    result = assistant.query("Which endpoint should I call to get a customer's order history?")
    print(result["answer"])
    print("\n--- Sources ---")
    for s in result["sources"]:
        print(f"[{s['score']:.3f}] {s['metadata'].get('source')} — {s['metadata'].get('method', '')} {s['metadata'].get('path', s['metadata'].get('title', ''))}")
