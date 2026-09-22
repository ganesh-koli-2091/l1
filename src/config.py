import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
OPENAPI_DIR = DATA_DIR / "openapi"
NOTES_DIR = DATA_DIR / "notes"
CHROMA_DIR = PROJECT_ROOT / "chroma_db"
CLAUDE_MD_PATH = PROJECT_ROOT / "CLAUDE.md"

EMBEDDING_MODEL = "all-MiniLM-L6-v2"
LLM_MODEL = "@azure-openai-eus2/gpt-5"
COLLECTION_NAME = "api_docs"
N_RESULTS = 5
# GPT-5 is a reasoning model — it consumes internal reasoning tokens before
# producing output. max_tokens is not supported; use max_completion_tokens
# with a budget large enough for both reasoning + visible answer.
MAX_COMPLETION_TOKENS = 4096

PORTKEY_BASE_URL = "https://portkeygateway.perficient.com/v1"
PORTKEY_API_KEY = os.getenv("PORTKEY_API_KEY", "")

# Fallback: set USE_DIRECT_ANTHROPIC=true and ANTHROPIC_API_KEY in .env
# to bypass the Portkey gateway and call Anthropic directly.
USE_DIRECT_ANTHROPIC = os.getenv("USE_DIRECT_ANTHROPIC", "false").lower() == "true"
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
DIRECT_LLM_MODEL = "claude-opus-4-5"


def validate_config() -> None:
    if USE_DIRECT_ANTHROPIC and not ANTHROPIC_API_KEY:
        raise EnvironmentError(
            "USE_DIRECT_ANTHROPIC=true but ANTHROPIC_API_KEY is not set in .env"
        )
    if not USE_DIRECT_ANTHROPIC and not PORTKEY_API_KEY:
        raise EnvironmentError(
            "PORTKEY_API_KEY is not set.\n"
            "Copy .env.example to .env and add your Portkey API key."
        )
