import time
from typing import Dict, Any, List, Optional
from config.settings import settings
from src.retrieval.retriever import TechnicalSupportRetriever, RetrievedChunk
from src.generation.llm import LLMClient, get_llm_client
from src.models.intent_classifier import IntentClassifier, get_intent_classifier
from src.database.mysql_db import DatabaseManager, get_db_manager
from src.utils.logger import get_logger

logger = get_logger(__name__)

class RAGPipeline:
    """End-to-end RAG pipeline executing:
    User Request -> Model Intent & Service Classification (<2ms) 
                 -> Semantic Retrieval from ChromaDB (<30ms) 
                 -> Grounded LLM / Extractive Generation 
                 -> Source Citation & MySQL Database Persistence.
    """

    def __init__(
        self,
        retriever: Optional[TechnicalSupportRetriever] = None,
        llm_client: Optional[LLMClient] = None,
        intent_classifier: Optional[IntentClassifier] = None,
        db_manager: Optional[DatabaseManager] = None
    ):
        self.retriever = retriever or TechnicalSupportRetriever()
        self.llm_client = llm_client or get_llm_client()
        self.intent_classifier = intent_classifier or get_intent_classifier()
        self.db = db_manager or get_db_manager()

    def get_rag_response(
        self,
        query: str,
        service_filter: Optional[str] = None,
        user_id: Optional[int] = None,
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        start_time = time.time()
        logger.info(f"Processing RAG pipeline query: '{query}'")

        # Step 1: Ultra-fast Model Intent & Service Classification (< 2ms)
        classification = self.intent_classifier.predict(query)
        predicted_intent = classification["intent"]
        predicted_service = classification["service"]
        urgency = classification["urgency"]
        is_oos = classification["is_out_of_scope"]

        logger.info(
            f"Model Prediction: Intent={predicted_intent} ({classification['intent_confidence']*100:.1f}%), "
            f"Service={predicted_service} ({classification['service_confidence']*100:.1f}%), "
            f"Urgency={urgency}, Model Latency={classification['latency_ms']}ms"
        )

        # Step 2: Instant Friendly Handling for Greetings and Conversational Queries
        if predicted_intent == "GREETING":
            q_lower = query.lower().strip()
            if any(w in q_lower for w in ["thank", "thanks", "appreciate"]):
                answer = (
                    "Hello! You're very welcome! 😊 I'm always glad to help.\n\n"
                    "If you encounter any other AWS issues with EC2, S3, Lambda, or IAM, please don't hesitate to ask. Have a fantastic day!"
                )
            elif any(w in q_lower for w in ["bye", "goodbye", "see you"]):
                answer = (
                    "Goodbye! 👋 Thank you for using the AWS Technical Support Assistant. "
                    "Whenever you need help troubleshooting or configuring AWS cloud infrastructure, I'll be here. Take care!"
                )
            elif any(w in q_lower for w in ["how are you", "how are you doing"]):
                answer = (
                    "Hello! 👋 I'm doing great, thank you for asking! I'm ready to help you with any AWS cloud challenges today.\n\n"
                    "Whether you're troubleshooting an EC2 instance, resolving an S3 NoSuchBucket error, optimizing a Lambda function, or configuring IAM security policies, what can I assist you with?"
                )
            elif any(w in q_lower for w in ["who are you", "what can you do"]):
                answer = (
                    "Hello! 👋 I am your dedicated **AWS Technical Support Assistant**.\n\n"
                    "I provide friendly, fast, and authoritative technical support for AWS Cloud infrastructure, including:\n"
                    "- 🖥️ **Amazon EC2**: SSH connectivity (`Permission denied`), status checks, EBS storage, security groups\n"
                    "- 🪣 **Amazon S3**: Bucket permissions (`AccessDenied`), `NoSuchBucket`, CORS, lifecycle rules\n"
                    "- ⚡ **AWS Lambda**: Timeouts, memory allocation, cold starts, private VPC networking\n"
                    "- 🛡️ **AWS IAM**: Least privilege permissions, trust policies, assume role errors, access keys\n\n"
                    "How can I help you today? Please feel free to ask your question!"
                )
            else:
                answer = (
                    "Hello! 👋 Welcome! I'm your AWS Technical Support Assistant, and I'm very glad to assist you today.\n\n"
                    "How can I help you with your AWS infrastructure? You can ask me to troubleshoot errors (e.g. SSH permission issues, S3 NoSuchBucket, Lambda timeouts), provide exact AWS CLI commands, or configure security policies."
                )

            latency_ms = round((time.time() - start_time) * 1000, 2)
            if user_id:
                try:
                    self.db.add_chat_entry(
                        user_id=user_id,
                        query=query,
                        response=answer,
                        intent="GREETING",
                        service="General AWS",
                        urgency=urgency,
                        is_grounded=True,
                        latency_ms=latency_ms,
                        sources=[],
                        session_id=session_id
                    )
                except Exception as e:
                    logger.error(f"Error persisting greeting entry to MySQL: {e}")

            return {
                "query": query,
                "answer": answer,
                "sources": [],
                "retrieved_documents": [],
                "classification": classification,
                "metadata": {
                    "latency_ms": latency_ms,
                    "is_grounded": True,
                    "provider": "FRIENDLY_GREETING_AGENT",
                    "total_retrieved": 0,
                    "top_k_used": 0,
                    "intent": "GREETING",
                    "predicted_service": "General AWS",
                    "urgency": urgency
                }
            }

        # Step 3: Instant Handling for Out-of-Scope Queries (Fast Guardrail Refusal)
        if is_oos and classification["intent_confidence"] >= 0.60:
            answer = (
                "### ☁️ AWS Technical Support Assistant\n\n"
                "**Notice**: Query Out-of-Scope\n\n"
                f"Your query appears to be related to **{predicted_service}** or outside the scope of AWS Cloud Technical Support. "
                "This assistant is strictly optimized for **Amazon Web Services (AWS)** infrastructure, specifically:\n"
                "- **Amazon EC2**: Instance troubleshooting, SSH connections, EBS volumes, status checks\n"
                "- **Amazon S3**: Bucket permissions, NoSuchBucket errors, CORS, lifecycle policies\n"
                "- **AWS Lambda**: Task timeouts, OOM errors, cold starts, concurrency, VPC ENI configurations\n"
                "- **AWS IAM**: Least privilege policies, roles, trust relationships, access keys, permissions\n\n"
                "*Please rephrase your question to target a supported AWS service or error.*"
            )
            latency_ms = round((time.time() - start_time) * 1000, 2)
            
            # Persist to MySQL if user_id is provided
            if user_id:
                self.db.add_chat_entry(
                    user_id=user_id,
                    query=query,
                    response=answer,
                    intent=predicted_intent,
                    service="Out-of-Scope",
                    urgency=urgency,
                    is_grounded=False,
                    latency_ms=latency_ms,
                    sources=[],
                    session_id=session_id
                )

            return {
                "query": query,
                "answer": answer,
                "sources": [],
                "retrieved_documents": [],
                "classification": classification,
                "metadata": {
                    "latency_ms": latency_ms,
                    "is_grounded": False,
                    "provider": "GUARDRAIL_FAST_REJECTION",
                    "total_retrieved": 0,
                    "top_k_used": 0,
                    "intent": predicted_intent,
                    "predicted_service": predicted_service,
                    "urgency": urgency
                }
            }

        # Step 3: Fast Dynamic Service Filtering
        effective_service_filter = service_filter
        if not effective_service_filter and predicted_service in settings.SUPPORTED_SERVICES and classification["service_confidence"] >= 0.70:
            # Softly boost or filter by predicted service if confident
            effective_service_filter = predicted_service

        # Step 4: Retrieve Context Chunks from ChromaDB
        retrieved_chunks = self.retriever.retrieve(query=query, service_filter=effective_service_filter)
        
        # If service-filtered retrieval yielded 0 chunks, fallback to unfiltered retrieval
        if not retrieved_chunks and effective_service_filter:
            logger.info("Service-filtered retrieval returned 0 chunks. Retrying across full knowledge base...")
            retrieved_chunks = self.retriever.retrieve(query=query, service_filter=None)

        # Step 5: Filter by similarity threshold
        relevant_chunks = self.retriever.filter_relevant_chunks(retrieved_chunks)
        
        # Determine grounding status
        is_grounded = len(relevant_chunks) > 0
        chunks_to_use = relevant_chunks if is_grounded else retrieved_chunks[:2] if retrieved_chunks else []

        # Step 6: LLM / Extractive Generation
        answer = self.llm_client.generate_response(query=query, context_chunks=chunks_to_use)

        # Step 7: Extract Source Citations
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
        logger.info(
            f"RAG Pipeline finished in {latency_ms}ms. Grounded: {is_grounded}, "
            f"Sources: {len(sources)}, Intent: {predicted_intent}"
        )

        # Step 8: Persist to MySQL / Database
        if user_id:
            try:
                self.db.add_chat_entry(
                    user_id=user_id,
                    query=query,
                    response=answer,
                    intent=predicted_intent,
                    service=predicted_service if predicted_service in settings.SUPPORTED_SERVICES else "General AWS",
                    urgency=urgency,
                    is_grounded=is_grounded,
                    latency_ms=latency_ms,
                    sources=sources,
                    session_id=session_id
                )
            except Exception as e:
                logger.error(f"Error persisting chat entry to MySQL: {e}")

        return {
            "query": query,
            "answer": answer,
            "sources": sources,
            "classification": classification,
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
                "top_k_used": len(chunks_to_use),
                "intent": predicted_intent,
                "predicted_service": predicted_service,
                "urgency": urgency,
                "classification_latency_ms": classification["latency_ms"]
            }
        }

_global_pipeline = None

def get_rag_pipeline() -> RAGPipeline:
    global _global_pipeline
    if _global_pipeline is None:
        _global_pipeline = RAGPipeline()
    return _global_pipeline
