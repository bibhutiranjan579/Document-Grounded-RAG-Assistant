import os
import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

# Prefer a project-local Hugging Face cache to avoid permission issues
CACHE_DIR = BASE_DIR / ".cache"
HF_HOME = os.getenv("HF_HOME", str(CACHE_DIR / "huggingface"))
TRANSFORMERS_CACHE = os.getenv("TRANSFORMERS_CACHE", str(CACHE_DIR / "transformers"))
XDG_CACHE_HOME = os.getenv("XDG_CACHE_HOME", str(CACHE_DIR))

os.environ.setdefault("HF_HOME", HF_HOME)
os.environ.setdefault("TRANSFORMERS_CACHE", TRANSFORMERS_CACHE)
os.environ.setdefault("XDG_CACHE_HOME", XDG_CACHE_HOME)

Path(HF_HOME).mkdir(parents=True, exist_ok=True)
Path(TRANSFORMERS_CACHE).mkdir(parents=True, exist_ok=True)
Path(XDG_CACHE_HOME).mkdir(parents=True, exist_ok=True)

dotenv_path = BASE_DIR / ".env"
if dotenv_path.exists():
    load_dotenv(dotenv_path)

DATA_DIR = BASE_DIR / "data" / "documents"
CHROMA_DIR = BASE_DIR / ".chromadb"

CHUNK_SIZE = 800
CHUNK_OVERLAP = 100
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
