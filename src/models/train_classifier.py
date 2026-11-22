import os
import time
import json
import pickle
from pathlib import Path
from typing import Dict, Any, Tuple

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report, accuracy_score

from config.settings import settings
from src.models.dataset import TRAINING_DATA
from src.utils.logger import get_logger

logger = get_logger(__name__)

class ModelTrainer:
    """Trains ultra-fast multi-target classifier models for technical query understanding."""

    def __init__(
        self,
        model_save_path: str = settings.INTENT_MODEL_PATH,
        metadata_save_path: str = settings.MODEL_METADATA_PATH
    ):
        self.model_save_path = Path(model_save_path)
        self.metadata_save_path = Path(metadata_save_path)
        self.model_save_path.parent.mkdir(parents=True, exist_ok=True)

    def train_models(self) -> Dict[str, Any]:
        """Trains Intent, Service, and Urgency classifiers and evaluates performance."""
        logger.info(f"Starting model training with {len(TRAINING_DATA)} annotated samples...")
        start_time = time.time()

        queries = [d["query"] for d in TRAINING_DATA]
        intents = [d["intent"] for d in TRAINING_DATA]
        services = [d["service"] for d in TRAINING_DATA]
        urgencies = [d["urgency"] for d in TRAINING_DATA]

        # Shared n-gram TF-IDF feature extractor optimized for sub-millisecond inference
        vectorizer = TfidfVectorizer(
            ngram_range=(1, 3),
            lowercase=True,
            max_features=5000,
            sublinear_tf=True
        )
        X_features = vectorizer.fit_transform(queries)

        # 1. Intent Classifier
        intent_clf = LogisticRegression(
            C=3.0,
            max_iter=1000,
            class_weight="balanced",
            random_state=42
        )
        intent_clf.fit(X_features, intents)
        intent_preds = intent_clf.predict(X_features)
        intent_acc = accuracy_score(intents, intent_preds)

        # 2. Service Classifier
        service_clf = LogisticRegression(
            C=3.0,
            max_iter=1000,
            class_weight="balanced",
            random_state=42
        )
        service_clf.fit(X_features, services)
        service_preds = service_clf.predict(X_features)
        service_acc = accuracy_score(services, service_preds)

        # 3. Urgency Classifier
        urgency_clf = LogisticRegression(
            C=2.0,
            max_iter=1000,
            class_weight="balanced",
            random_state=42
        )
        urgency_clf.fit(X_features, urgencies)
        urgency_preds = urgency_clf.predict(X_features)
        urgency_acc = accuracy_score(urgencies, urgency_preds)

        # Measure single-query latency benchmark
        test_q = ["How do I fix a NoSuchBucket error in Amazon S3?"]
        latencies = []
        for _ in range(50):
            t0 = time.perf_counter()
            f = vectorizer.transform(test_q)
            _ = intent_clf.predict_proba(f)
            _ = service_clf.predict_proba(f)
            _ = urgency_clf.predict(f)
            latencies.append((time.perf_counter() - t0) * 1000)
        avg_latency_ms = round(sum(latencies) / len(latencies), 3)

        total_training_time = round(time.time() - start_time, 2)
        logger.info(
            f"Training finished in {total_training_time}s! "
            f"Intent Acc: {intent_acc*100:.1f}%, Service Acc: {service_acc*100:.1f}%, "
            f"Avg Inference Latency: {avg_latency_ms}ms"
        )

        # Bundle model artifacts
        bundle = {
            "vectorizer": vectorizer,
            "intent_clf": intent_clf,
            "service_clf": service_clf,
            "urgency_clf": urgency_clf,
            "intent_classes": list(intent_clf.classes_),
            "service_classes": list(service_clf.classes_),
            "urgency_classes": list(urgency_clf.classes_),
            "trained_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "total_samples": len(TRAINING_DATA)
        }

        # Save model pickle
        with open(self.model_save_path, "wb") as f:
            pickle.dump(bundle, f)
        logger.info(f"Model artifact saved to: {self.model_save_path}")

        # Save metadata JSON
        metadata = {
            "model_name": "AWSSupportIntentClassifier-v2",
            "algorithm": "TFIDF_LogisticRegression_Ensemble",
            "total_samples": len(TRAINING_DATA),
            "intent_accuracy": round(intent_acc, 4),
            "service_accuracy": round(service_acc, 4),
            "urgency_accuracy": round(urgency_acc, 4),
            "avg_inference_latency_ms": avg_latency_ms,
            "intents": list(intent_clf.classes_),
            "services": list(service_clf.classes_),
            "urgencies": list(urgency_clf.classes_),
            "trained_at": bundle["trained_at"]
        }
        with open(self.metadata_save_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2)
        logger.info(f"Model metadata saved to: {self.metadata_save_path}")

        return metadata

def train_and_save_model() -> Dict[str, Any]:
    trainer = ModelTrainer()
    return trainer.train_models()

if __name__ == "__main__":
    train_and_save_model()

