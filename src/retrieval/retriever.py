from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

from config.settings import settings
from src.vectorstore.chroma_store import ChromaVectorStore, get_vector_store
from src.utils.logger import get_logger

logger = get_logger(__name__)

class RetrievedChunk(BaseModel):
    chunk_id: str
    content: str
    title: str
    service: str
    category: str
    source: str
    url: str
    distance: float
    relevance_score: float  # Cosine similarity: 1.0 - distance
    metadata: Dict[str, Any] = Field(default_factory=dict)

class TechnicalSupportRetriever:
    """Retriever engine fetching context from ChromaDB with score filtering."""

    def __init__(
        self,
        vector_store: Optional[ChromaVectorStore] = None,
        top_k: int = settings.TOP_K,
        similarity_threshold: float = settings.SIMILARITY_THRESHOLD
    ):
        self.vector_store = vector_store or get_vector_store()
        self.top_k = top_k
        self.similarity_threshold = similarity_threshold

    def retrieve(
        self,
        query: str,
        top_k: Optional[int] = None,
        service_filter: Optional[str] = None
    ) -> List[RetrievedChunk]:
        k = top_k or self.top_k
        where_filter = None
        if service_filter:
            where_filter = {"service": service_filter}

        logger.info(f"Retrieving top {k} chunks for query: '{query}'")
        raw_results = self.vector_store.query(query_text=query, n_results=k, where_filter=where_filter)

        retrieved_chunks: List[RetrievedChunk] = []

        ids = raw_results.get("ids", [[]])[0]
        documents = raw_results.get("documents", [[]])[0]
        metadatas = raw_results.get("metadatas", [[]])[0]
        distances = raw_results.get("distances", [[]])[0]

        for chunk_id, doc_content, meta, dist in zip(ids, documents, metadatas, distances):
            # For cosine space in ChromaDB, distance is in range [0, 2]. Similarity = max(0, 1 - distance)
            rel_score = max(0.0, float(1.0 - dist))
            
            chunk = RetrievedChunk(
                chunk_id=chunk_id,
                content=doc_content,
                title=meta.get("title", "AWS Documentation"),
                service=meta.get("service", "General AWS"),
                category=meta.get("category", "Technical Guide"),
                source=meta.get("source", "AWS Knowledge Base"),
                url=meta.get("url", ""),
                distance=float(dist),
                relevance_score=rel_score,
                metadata=meta
            )
            retrieved_chunks.append(chunk)

        # Sort by highest relevance score
        retrieved_chunks.sort(key=lambda x: x.relevance_score, reverse=True)
        logger.info(f"Retrieved {len(retrieved_chunks)} relevant context chunks.")
        return retrieved_chunks

    def filter_relevant_chunks(self, chunks: List[RetrievedChunk]) -> List[RetrievedChunk]:
        """Filters out chunks below configured similarity threshold."""
        return [c for c in chunks if c.relevance_score >= self.similarity_threshold]
