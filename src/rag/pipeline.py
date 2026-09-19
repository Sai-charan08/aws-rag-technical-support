import time
from typing import Dict, Any, List, Optional
from config.settings import settings
from src.retrieval.retriever import TechnicalSupportRetriever, RetrievedChunk
from src.generation.llm import LLMClient, get_llm_client
from src.utils.logger import get_logger

logger = get_logger(__name__)

class RAGPipeline:
    """End-to-end RAG pipeline executing Query -> Retrieval -> Grounding -> LLM Generation -> Citation."""

    def __init__(
        self,
        retriever: Optional[TechnicalSupportRetriever] = None,
        llm_client: Optional[LLMClient] = None
    ):
        self.retriever = retriever or TechnicalSupportRetriever()
        self.llm_client = llm_client or get_llm_client()

    def get_rag_response(self, query: str, service_filter: Optional[str] = None) -> Dict[str, Any]:
        start_time = time.time()
        logger.info(f"Processing RAG pipeline query: '{query}'")

        # Step 1: Retrieve context chunks
        retrieved_chunks = self.retriever.retrieve(query=query, service_filter=service_filter)
        
        # Step 2: Filter by similarity threshold
        relevant_chunks = self.retriever.filter_relevant_chunks(retrieved_chunks)
        
        # Determine grounding status
        is_grounded = len(relevant_chunks) > 0
        chunks_to_use = relevant_chunks if is_grounded else retrieved_chunks[:2] if retrieved_chunks else []

        # Step 3: LLM Answer Generation
        answer = self.llm_client.generate_response(query=query, context_chunks=chunks_to_use)

        # Step 4: Extract Source Citations
        sources = []
        seen_sources = set()
        for chunk in chunks_to_use:
            src_key = f"{chunk.title}_{chunk.source}"
            if src_key not in seen_sources:
                seen_sources.add(src_key)
                sources.append({
                    "title": chunk.title,
                    "service": chunk.service,
                    "source": chunk.source,
                    "url": chunk.url,
                    "relevance_score": chunk.relevance_score
                })

        latency_ms = round((time.time() - start_time) * 1000, 2)
        logger.info(f"RAG Pipeline finished in {latency_ms}ms. Grounded: {is_grounded}, Sources: {len(sources)}")

        return {
            "query": query,
            "answer": answer,
            "sources": sources,
            "retrieved_documents": [
                {
                    "chunk_id": c.chunk_id,
                    "content": c.content,
                    "title": c.title,
                    "service": c.service,
                    "source": c.source,
                    "url": c.url,
                    "relevance_score": c.relevance_score,
                    "distance": c.distance
                }
                for c in chunks_to_use
            ],
            "metadata": {
                "latency_ms": latency_ms,
                "is_grounded": is_grounded,
                "provider": self.llm_client.provider,
                "total_retrieved": len(retrieved_chunks),
                "top_k_used": len(chunks_to_use)
            }
        }

_global_pipeline = None

def get_rag_pipeline() -> RAGPipeline:
    global _global_pipeline
    if _global_pipeline is None:
        _global_pipeline = RAGPipeline()
    return _global_pipeline
