import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

class Config:
    # Database
    DATABASE_URL = os.getenv(
        "DATABASE_URL",
        "postgresql://rag_user:rag_password@localhost:5432/rag_db"
    ).strip().replace("'", "").replace('"', "")
    
    # API
    SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 30
    
    # URLs
    BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
    FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")
    
    # Paths
    BASE_DIR = Path(__file__).parent
    DATA_DIR = BASE_DIR / "data"
    RAW_DIR = DATA_DIR / "raw"
    PROCESSED_DIR = DATA_DIR / "processed"
    INDEXES_DIR = DATA_DIR / "indexes"
    LOGS_DIR = BASE_DIR / "logs"
    
    # Create directories
    for dir_path in [DATA_DIR, RAW_DIR, PROCESSED_DIR, INDEXES_DIR, LOGS_DIR]:
        dir_path.mkdir(parents=True, exist_ok=True)
    
    # Gemini
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

    # RAG Configuration
    RAG_CONFIG = {
        "chunking": {
            "chunk_size": 512,
            "overlap": 50
        },
        "embedding": {
            "model_name": "sentence-transformers/all-MiniLM-L6-v2",
            "batch_size": 32
        },
        "retrieval": {
            "k_retrieve": 10,
            "k_rerank": 5,
            "use_reranker": True
        },
        "generation": {
            "model_name": "models/gemini-pro-latest",
            "max_new_tokens": 1024,
            "temperature": 0.3
        },
        "verification": {
            "similarity_threshold": 0.1,
            "confidence_threshold": 0.7
        }
    }
    
    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE = LOGS_DIR / "rag_system.log"

config = Config()