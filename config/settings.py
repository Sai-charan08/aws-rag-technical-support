import os
from pathlib import Path
from pydantic import ConfigDict
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    PROJECT_NAME: str = "AWS Technical Support RAG Assistant"
    VERSION: str = "2.0.0"
    
    # Paths
    BASE_DIR: Path = BASE_DIR
    DATA_DIR: Path = BASE_DIR / "data"
    SAMPLE_DATA_DIR: Path = BASE_DIR / "data" / "sample"
    RAW_DATA_DIR: Path = BASE_DIR / "data" / "raw"
    PROCESSED_DATA_DIR: Path = BASE_DIR / "data" / "processed"
    MODELS_DIR: Path = BASE_DIR / "models"
    CHROMA_DB_PATH: str = os.getenv("CHROMA_DB_PATH", str(BASE_DIR / "chroma_db"))
    COLLECTION_NAME: str = os.getenv("COLLECTION_NAME", "aws_technical_support")
    
    # MySQL Database Settings
    MYSQL_HOST: str = os.getenv("MYSQL_HOST", "127.0.0.1")
    MYSQL_PORT: int = int(os.getenv("MYSQL_PORT", "3307"))
    MYSQL_USER: str = os.getenv("MYSQL_USER", "root")
    MYSQL_PASSWORD: str = os.getenv("MYSQL_PASSWORD", "")
    MYSQL_DATABASE: str = os.getenv("MYSQL_DATABASE", "aws_support_rag")
    DB_FALLBACK_SQLITE: bool = os.getenv("DB_FALLBACK_SQLITE", "false").lower() in ("true", "1", "yes")
    SQLITE_FALLBACK_PATH: str = os.getenv(
        "SQLITE_FALLBACK_PATH", str(BASE_DIR / "data" / "support_database.sqlite")
    )

    # Auth & Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "aws-support-rag-super-secure-key-2026")
    SESSION_EXPIRY_MINUTES: int = int(os.getenv("SESSION_EXPIRY_MINUTES", "1440"))

    # Intent Classifier Model Settings
    INTENT_MODEL_PATH: str = os.getenv(
        "INTENT_MODEL_PATH", str(BASE_DIR / "models" / "intent_classifier.pkl")
    )
    MODEL_METADATA_PATH: str = os.getenv(
        "MODEL_METADATA_PATH", str(BASE_DIR / "models" / "model_metadata.json")
    )

    # LLM Settings
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "demo")  # "demo", "openai", "gemini"
    LLM_MODEL: str = os.getenv("LLM_MODEL", "gpt-4o-mini")
    
    # Embeddings
    EMBEDDING_MODEL_NAME: str = os.getenv(
        "EMBEDDING_MODEL_NAME", "sentence-transformers/all-MiniLM-L6-v2"
    )
    
    # Retrieval
    TOP_K: int = int(os.getenv("TOP_K", "5"))
    SIMILARITY_THRESHOLD: float = float(os.getenv("SIMILARITY_THRESHOLD", "0.35"))
    
    # Chunking
    CHUNK_SIZE: int = 600
    CHUNK_OVERLAP: int = 100
    
    # Supported Scope
    SUPPORTED_SERVICES: list = ["Amazon EC2", "Amazon S3", "AWS Lambda", "AWS IAM"]
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    model_config = ConfigDict(env_file=".env", extra="ignore")

settings = Settings()
