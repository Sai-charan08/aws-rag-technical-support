import os
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings as ChromaSettings

from config.settings import settings
from src.embeddings.embedding_model import get_embedding_function
from src.ingestion.chunker import DocumentChunk
from src.utils.logger import get_logger

logger = get_logger(__name__)

class ChromaVectorStore:
    """Persistent ChromaDB vector store wrapper."""

    def __init__(
        self,
        persist_directory: str = settings.CHROMA_DB_PATH,
        collection_name: str = settings.COLLECTION_NAME
    ):
        self.persist_directory = persist_directory
        self.collection_name = collection_name
        self.embedding_function = get_embedding_function()
        
        os.makedirs(self.persist_directory, exist_ok=True)
        
        logger.info(f"Initializing persistent ChromaDB client at: {self.persist_directory}")
        self.client = chromadb.PersistentClient(path=self.persist_directory)
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            embedding_function=self.embedding_function,
            metadata={"hnsw:space": "cosine"}
        )

    def add_chunks(self, chunks: List[DocumentChunk]):
        if not chunks:
            logger.warning("No chunks provided to add to vector store.")
            return

        ids = [chunk.chunk_id for chunk in chunks]
        documents = [chunk.content for chunk in chunks]
        metadatas = []
        
        for chunk in chunks:
            # Flatten metadata values to scalar strings/ints/floats for ChromaDB compatibility
            meta = {
                "chunk_id": chunk.chunk_id,
                "parent_doc_id": chunk.parent_doc_id,
                "title": chunk.title,
                "service": chunk.service,
                "category": chunk.category,
                "source": chunk.source,
                "url": chunk.url or "",
                "chunk_index": chunk.chunk_index,
                "total_chunks": chunk.total_chunks
            }
            metadatas.append(meta)

        logger.info(f"Upserting {len(chunks)} document chunks into ChromaDB collection '{self.collection_name}'...")
        self.collection.upsert(
            ids=ids,
            documents=documents,
            metadatas=metadatas
        )
        logger.info(f"Successfully upserted {len(chunks)} chunks.")

    def query(
        self,
        query_text: str,
        n_results: int = settings.TOP_K,
        where_filter: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Perform cosine similarity search against persistent vector store."""
        if not query_text or not query_text.strip():
            return {"ids": [[]], "documents": [[]], "metadatas": [[]], "distances": [[]]}

        kwargs = {
            "query_texts": [query_text],
            "n_results": n_results,
            "include": ["documents", "metadatas", "distances"]
        }
        if where_filter:
            kwargs["where"] = where_filter

        results = self.collection.query(**kwargs)
        return results

    def count(self) -> int:
        return self.collection.count()

    def rebuild(self):
        """Delete existing collection and recreate clean database."""
        logger.warning(f"Rebuilding ChromaDB collection '{self.collection_name}'...")
        self.client.delete_collection(name=self.collection_name)
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            embedding_function=self.embedding_function,
            metadata={"hnsw:space": "cosine"}
        )

    def get_stats(self) -> Dict[str, Any]:
        count = self.count()
        return {
            "collection_name": self.collection_name,
            "persist_directory": self.persist_directory,
            "total_chunks": count,
            "status": "Ready" if count > 0 else "Empty"
        }

_global_vector_store = None

def get_vector_store() -> ChromaVectorStore:
    global _global_vector_store
    if _global_vector_store is None:
        _global_vector_store = ChromaVectorStore()
    return _global_vector_store
