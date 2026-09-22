"""
Ingestion pipeline: Load → Chunk → Embed → Store

Run:
    python src/ingest.py          # skip if already populated
    python src/ingest.py --reset  # wipe and re-ingest
"""

import argparse
import sys
from pathlib import Path

import yaml
import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

sys.path.insert(0, str(Path(__file__).parent))
from config import (
    OPENAPI_DIR, NOTES_DIR, CHROMA_DIR,
    EMBEDDING_MODEL, COLLECTION_NAME,
)


def _format_endpoint_chunk(service_name: str, method: str, path: str, operation: dict) -> str:
    """Build a single text chunk representing one API endpoint."""
    summary = operation.get("summary", "")
    description = operation.get("description", "")

    params_lines = []
    for param in operation.get("parameters", []):
        required = "required" if param.get("required") else "optional"
        desc = param.get("description", "")
        schema = param.get("schema", {})
        ptype = schema.get("type", "string")
        params_lines.append(
            f"  - {param['name']} ({param.get('in', 'query')}, {required}, {ptype}): {desc}"
        )
    params_text = "\n".join(params_lines) if params_lines else "  None"

    # Request body fields
    body_lines = []
    body = operation.get("requestBody", {})
    if body:
        content = body.get("content", {}).get("application/json", {})
        schema = content.get("schema", {})
        required_fields = schema.get("required", [])
        props = schema.get("properties", {})
        for field, details in props.items():
            req = "required" if field in required_fields else "optional"
            fdesc = details.get("description", "")
            ftype = details.get("type", "")
            body_lines.append(f"  - {field} ({req}, {ftype}): {fdesc}")
    body_text = "\n".join(body_lines) if body_lines else "  None"

    # Response schema — top-level properties of 200/201 response
    response_lines = []
    responses = operation.get("responses", {})
    for code in ("200", "201"):
        if code in responses:
            resp_content = responses[code].get("content", {}).get("application/json", {})
            resp_schema = resp_content.get("schema", {})
            resp_props = resp_schema.get("properties", {})
            for field, details in list(resp_props.items())[:6]:  # cap at 6 fields
                ftype = details.get("type", "")
                fdesc = details.get("description", "")
                response_lines.append(f"  - {field} ({ftype}): {fdesc}")
            break
    response_text = "\n".join(response_lines) if response_lines else "  See spec"

    tags = ", ".join(operation.get("tags", []))
    auth = "Yes — Authorization: Bearer <token>" if operation.get("security") else "No"

    return (
        f"Service: {service_name}\n"
        f"Endpoint: {method.upper()} {path}\n"
        f"Summary: {summary}\n"
        f"Description: {description}\n"
        f"Parameters:\n{params_text}\n"
        f"Request body fields:\n{body_text}\n"
        f"Response fields:\n{response_text}\n"
        f"Authentication required: {auth}\n"
        f"Tags: {tags}"
    )


def load_openapi_docs() -> list[dict]:
    docs = []
    for yaml_file in sorted(OPENAPI_DIR.glob("*.yaml")):
        with open(yaml_file, encoding="utf-8") as f:
            spec = yaml.safe_load(f)

        service_name = spec.get("info", {}).get("title", yaml_file.stem)
        paths = spec.get("paths", {})

        for path, path_item in paths.items():
            for method, operation in path_item.items():
                if method not in ("get", "post", "put", "patch", "delete"):
                    continue
                chunk_text = _format_endpoint_chunk(service_name, method, path, operation)
                doc_id = f"{yaml_file.stem}::{method.upper()}::{path}"
                docs.append({
                    "id": doc_id,
                    "text": chunk_text,
                    "metadata": {
                        "source": yaml_file.name,
                        "service": service_name,
                        "method": method.upper(),
                        "path": path,
                        "type": "endpoint",
                    },
                })
    return docs


def load_notes_docs() -> list[dict]:
    docs = []
    for md_file in sorted(NOTES_DIR.glob("*.md")):
        content = md_file.read_text(encoding="utf-8")

        # Split by H1 and H2 headers
        sections: list[tuple[str, str]] = []
        current_title = md_file.stem
        current_lines: list[str] = []

        for line in content.splitlines():
            if line.startswith("## ") or line.startswith("# "):
                if current_lines:
                    sections.append((current_title, "\n".join(current_lines)))
                current_title = line.lstrip("#").strip()
                current_lines = [line]
            else:
                current_lines.append(line)

        if current_lines:
            sections.append((current_title, "\n".join(current_lines)))

        for i, (title, text) in enumerate(sections):
            if len(text.strip()) < 30:
                continue
            doc_id = f"{md_file.stem}::section::{i}"
            docs.append({
                "id": doc_id,
                "text": text.strip(),
                "metadata": {
                    "source": md_file.name,
                    "title": title,
                    "type": "note",
                },
            })
    return docs


def ingest(reset: bool = False) -> None:
    ef = SentenceTransformerEmbeddingFunction(model_name=EMBEDDING_MODEL)
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))

    if reset:
        try:
            client.delete_collection(COLLECTION_NAME)
            print(f"[reset] Deleted existing collection '{COLLECTION_NAME}'")
        except Exception:
            pass

    existing = [c.name for c in client.list_collections()]
    if COLLECTION_NAME in existing and not reset:
        col = client.get_collection(COLLECTION_NAME, embedding_function=ef)
        count = col.count()
        if count > 0:
            print(f"Collection '{COLLECTION_NAME}' already has {count} documents. Use --reset to re-ingest.")
            return

    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=ef,
        metadata={"hnsw:space": "cosine"},
    )

    print("Loading OpenAPI endpoint documents...")
    endpoint_docs = load_openapi_docs()
    print(f"  {len(endpoint_docs)} endpoint chunks loaded")

    print("Loading architecture notes documents...")
    notes_docs = load_notes_docs()
    print(f"  {len(notes_docs)} note chunks loaded")

    all_docs = endpoint_docs + notes_docs
    print(f"\nEmbedding and storing {len(all_docs)} total chunks (this may take 30–60s on first run)...")

    # ChromaDB add in batches of 100
    batch_size = 100
    for i in range(0, len(all_docs), batch_size):
        batch = all_docs[i:i + batch_size]
        collection.add(
            ids=[d["id"] for d in batch],
            documents=[d["text"] for d in batch],
            metadatas=[d["metadata"] for d in batch],
        )
        print(f"  Stored batch {i // batch_size + 1}/{(len(all_docs) - 1) // batch_size + 1}")

    print(f"\nIngestion complete. Total documents stored: {collection.count()}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ingest API docs into ChromaDB")
    parser.add_argument("--reset", action="store_true", help="Wipe and re-ingest all documents")
    args = parser.parse_args()
    ingest(reset=args.reset)
