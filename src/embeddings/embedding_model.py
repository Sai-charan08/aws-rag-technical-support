from typing import List
from sentence_transformers import SentenceTransformer
from chromadb.api.types import EmbeddingFunction
from config.settings import settings
from src.utils.logger import get_logger

logger = get_logger(__name__)

class SentenceTransformerEmbeddingFunction(EmbeddingFunction):
    """ChromaDB compatible embedding function using SentenceTransformers."""
    
    def __init__(self, model_name: str = settings.EMBEDDING_MODEL_NAME):
        self.model_name = model_name
        logger.info(f"Loading SentenceTransformer embedding model: {self.model_name}")
        self.model = SentenceTransformer(self.model_name)

    def name(self) -> str:
        return f"SentenceTransformerEmbeddingFunction_{self.model_name}"

    def __call__(self, input: List[str]) -> List[List[float]]:
        embeddings = self.model.encode(input, normalize_embeddings=True)
        return embeddings.tolist()

class EmbeddingManager:
    """Singleton-style wrapper for managing local embedding generation."""
    _instance = None
    _embedding_function = None

    def __new__(cls, model_name: str = settings.EMBEDDING_MODEL_NAME):
        if cls._instance is None:
            cls._instance = super(EmbeddingManager, cls).__new__(cls)
            cls._embedding_function = SentenceTransformerEmbeddingFunction(model_name)
        return cls._instance

    @property
    def embedding_function(self) -> EmbeddingFunction:
        return self._embedding_function

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return self._embedding_function(texts)

    def embed_query(self, query: str) -> List[float]:
        return self._embedding_function([query])[0]

def get_embedding_function() -> EmbeddingFunction:
    """Helper factory returning ChromaDB embedding function."""
    manager = EmbeddingManager()
    return manager.embedding_function
