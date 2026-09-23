import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

# Paths
DATA_DIR = BASE_DIR / "data"

# Allow overriding the database via environment variable
_env_db = os.getenv("TALK2DB_DB_PATH")
if _env_db:
    DATABASE_PATH = Path(_env_db)
else:
    DATABASE_PATH = DATA_DIR / "chinook.db"

# SQLite read-only connection URI
SQLITE_RO_URI = f"file:{DATABASE_PATH}?mode=ro"

# API Metadata
APP_TITLE = "Talk2DB"
APP_DESCRIPTION = "Natural language interface for read-only databases"
APP_VERSION = "0.2.0"

# LLM Configuration
GROQ_API_KEY = os.getenv("groq_api_1")
GROQ_MODEL = "openai/gpt-oss-120b"
GROQ_MAX_TOKENS = 1024
GROQ_TEMPERATURE = 0.0  # Deterministic SQL generation
