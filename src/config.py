# src/config.py
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
VECTOR_STORE_DIR = BASE_DIR / "chroma_db"

GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY não encontrada no arquivo .env")

MODEL_NAME = "gemini-2.0-flash"
EMBEDDING_MODEL = "models/text-embedding-004"

## Configurações do RAG
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
TOP_K_RESULTS = 5

COMPLIANCE_FILE = DATA_DIR / "politica_compliance.txt"

if __name__ == "__main__":
    print(f"Configurações carregadas:\n- GOOGLE_API_KEY: {'*' * 8 + GOOGLE_API_KEY[-4:]}\n- MODEL_NAME: {MODEL_NAME}\n- EMBEDDING_MODEL: {EMBEDDING_MODEL}\n- DATA_DIR: {DATA_DIR}\n- VECTOR_STORE_DIR: {VECTOR_STORE_DIR}")
