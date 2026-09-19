import sys
import json
from pathlib import Path

# Add workspace root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.evaluation.evaluation import RAGEvaluator
from src.utils.logger import get_logger

logger = get_logger(__name__)

def main():
    logger.info("=== Starting RAG Evaluation Script ===")
    evaluator = RAGEvaluator()
    summary = evaluator.evaluate_benchmark()

    print("\n" + "=" * 60)
    print("        AWS RAG TECHNICAL SUPPORT ASSISTANT - BENCHMARK REPORT")
    print("=" * 60)
    print(f"Total Benchmark Queries evaluated : {summary['total_questions']}")
    print(f"Hit Rate @ K                       : {summary['hit_rate_at_k_percent']}%")
    print(f"Mean Reciprocal Rank (MRR)         : {summary['mrr']}")
    print(f"Grounded Context Rate              : {summary['grounded_rate_percent']}%")
    print(f"Average Response Latency           : {summary['avg_latency_ms']} ms")
    print("=" * 60 + "\n")

    # Save summary report artifact
    report_file = Path(__file__).resolve().parent.parent / "data" / "evaluation_report.json"
    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    logger.info(f"Evaluation report saved to: {report_file}")

if __name__ == "__main__":
    main()
