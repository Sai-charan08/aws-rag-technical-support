import json
import time
from pathlib import Path
from typing import List, Dict, Any
from config.settings import settings
from src.rag.pipeline import RAGPipeline, get_rag_pipeline
from src.utils.logger import get_logger

logger = get_logger(__name__)

class RAGEvaluator:
    """Benchmark evaluation engine for measuring RAG retrieval & generation quality."""

    def __init__(self, pipeline: RAGPipeline = None):
        self.pipeline = pipeline or get_rag_pipeline()
        self.test_questions_file = Path(__file__).parent / "test_questions.json"

    def load_test_questions(self) -> List[Dict[str, Any]]:
        with open(self.test_questions_file, "r", encoding="utf-8") as f:
            return json.load(f)

    def evaluate_benchmark(self) -> Dict[str, Any]:
        questions = self.load_test_questions()
        logger.info(f"Loaded {len(questions)} evaluation test questions.")

        total_questions = len(questions)
        retrieval_hits = 0
        reciprocal_ranks = []
        latencies = []
        grounded_count = 0
        detailed_results = []

        for idx, q_item in enumerate(questions, 1):
            q_id = q_item["id"]
            question = q_item["question"]
            category = q_item["category"]
            keywords = q_item.get("keywords", [])
            expected_service = q_item.get("expected_service")

            start_t = time.time()
            rag_res = self.pipeline.get_rag_response(question)
            exec_time = (time.time() - start_t) * 1000
            latencies.append(exec_time)

            retrieved_docs = rag_res.get("retrieved_documents", [])
            is_grounded = rag_res.get("metadata", {}).get("is_grounded", False)
            if is_grounded:
                grounded_count += 1

            # Check Hit Rate @ K and Reciprocal Rank
            hit_found = False
            rank_found = 0

            for r_idx, doc in enumerate(retrieved_docs, 1):
                doc_text = (doc.get("content", "") + " " + doc.get("title", "")).lower()
                matches_keyword = any(kw.lower() in doc_text for kw in keywords)
                
                if matches_keyword or (expected_service and expected_service.lower() in doc.get("service", "").lower()):
                    if not hit_found:
                        hit_found = True
                        rank_found = r_idx
                        break

            if hit_found:
                retrieval_hits += 1
                reciprocal_ranks.append(1.0 / rank_found)
            else:
                reciprocal_ranks.append(0.0)

            detailed_results.append({
                "id": q_id,
                "question": question,
                "category": category,
                "hit": hit_found,
                "rank": rank_found,
                "is_grounded": is_grounded,
                "latency_ms": round(exec_time, 2),
                "num_sources": len(rag_res.get("sources", []))
            })

        hit_rate_at_k = (retrieval_hits / total_questions) * 100 if total_questions else 0
        mrr = sum(reciprocal_ranks) / total_questions if total_questions else 0
        avg_latency = sum(latencies) / total_questions if total_questions else 0
        grounded_rate = (grounded_count / total_questions) * 100 if total_questions else 0

        summary = {
            "total_questions": total_questions,
            "hit_rate_at_k_percent": round(hit_rate_at_k, 2),
            "mrr": round(mrr, 4),
            "avg_latency_ms": round(avg_latency, 2),
            "grounded_rate_percent": round(grounded_rate, 2),
            "top_k_evaluated": settings.TOP_K,
            "detailed_results": detailed_results
        }

        logger.info(f"Evaluation Complete! Hit Rate: {hit_rate_at_k:.2f}%, MRR: {mrr:.4f}, Avg Latency: {avg_latency:.2f}ms")
        return summary
