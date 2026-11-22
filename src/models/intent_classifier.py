import os
import time
import pickle
import json
from pathlib import Path
from typing import Dict, Any, Optional

from config.settings import settings
from src.utils.logger import get_logger

logger = get_logger(__name__)

class IntentClassifier:
    """Production Inference Model for Technical Support Query Understanding.
    
    Accepts user requests, analyzes intent, identifies target AWS services,
    assesses urgency, and routes them to the fast RAG pipeline.
    Runs with ultra-low latency (< 2ms per query).
    """

    def __init__(self, model_path: str = settings.INTENT_MODEL_PATH):
        self.model_path = Path(model_path)
        self.vectorizer = None
        self.intent_clf = None
        self.service_clf = None
        self.urgency_clf = None
        self.metadata = {}
        self._load_or_train_model()

    def _load_or_train_model(self):
        """Loads model artifact from disk or initiates training if absent."""
        if not self.model_path.exists():
            logger.warning(f"Model file not found at '{self.model_path}'. Initiating automatic training...")
            from src.models.train_classifier import train_and_save_model
            train_and_save_model()

        try:
            with open(self.model_path, "rb") as f:
                bundle = pickle.load(f)
            self.vectorizer = bundle["vectorizer"]
            self.intent_clf = bundle["intent_clf"]
            self.service_clf = bundle["service_clf"]
            self.urgency_clf = bundle["urgency_clf"]
            logger.info("IntentClassifier model successfully loaded into memory!")

            meta_file = Path(settings.MODEL_METADATA_PATH)
            if meta_file.exists():
                with open(meta_file, "r", encoding="utf-8") as mf:
                    self.metadata = json.load(mf)
        except Exception as e:
            logger.error(f"Error loading model bundle: {e}. Falling back to rule-based classification.")

    def predict(self, query: str) -> Dict[str, Any]:
        """Classifies user technical request with sub-millisecond execution time."""
        start_time = time.perf_counter()

        # Handle empty/short queries gracefully
        if not query or not query.strip():
            return {
                "intent": "CONCEPTUAL_EXPLANATION",
                "intent_confidence": 0.5,
                "service": "General AWS",
                "service_confidence": 0.5,
                "urgency": "LOW",
                "is_out_of_scope": False,
                "recommended_action": "Request more details from the user.",
                "latency_ms": 0.05
            }

        # If model failed to load, fallback to heuristics
        if not self.vectorizer or not self.intent_clf:
            return self._heuristic_fallback(query, start_time)

        try:
            features = self.vectorizer.transform([query])

            # 1. Intent probabilities
            intent_probs = self.intent_clf.predict_proba(features)[0]
            top_intent_idx = intent_probs.argmax()
            predicted_intent = self.intent_clf.classes_[top_intent_idx]
            intent_conf = float(intent_probs[top_intent_idx])

            # 2. Service probabilities
            service_probs = self.service_clf.predict_proba(features)[0]
            top_service_idx = service_probs.argmax()
            predicted_service = self.service_clf.classes_[top_service_idx]
            service_conf = float(service_probs[top_service_idx])

            # 3. Urgency
            predicted_urgency = self.urgency_clf.predict(features)[0]

            # Fast domain heuristic overrides for obvious keywords
            q_lower = query.lower().strip()
            greetings = ["hello", "hi", "hey", "hello there", "hi there", "good morning", "good afternoon", "good evening", "how are you", "who are you", "what can you do", "thank you", "thanks", "bye", "goodbye"]
            if q_lower in greetings or any(q_lower.startswith(g + " ") for g in ["hello", "hi", "hey", "good morning"]):
                predicted_intent = "GREETING"
                predicted_service = "General AWS"
                predicted_urgency = "LOW"
                intent_conf = 0.99
                service_conf = 0.99
            elif "azure" in q_lower or "gcp" in q_lower or "google cloud" in q_lower or "recipe" in q_lower or "world cup" in q_lower:
                predicted_intent = "OUT_OF_SCOPE"
                predicted_service = "Out-of-Scope"
                intent_conf = 0.99
                service_conf = 0.99
            elif "ec2" in q_lower or "ssh" in q_lower or "instance" in q_lower:
                if predicted_service in ["Out-of-Scope", "General AWS"]:
                    predicted_service = "Amazon EC2"
            elif "s3" in q_lower or "bucket" in q_lower:
                if predicted_service in ["Out-of-Scope", "General AWS"]:
                    predicted_service = "Amazon S3"
            elif "lambda" in q_lower or "cold start" in q_lower or "timeout" in q_lower:
                if predicted_service in ["Out-of-Scope", "General AWS"]:
                    predicted_service = "AWS Lambda"
            elif "iam" in q_lower or "least privilege" in q_lower or "policy" in q_lower or "role" in q_lower:
                if predicted_service in ["Out-of-Scope", "General AWS"]:
                    predicted_service = "AWS IAM"

            is_out_of_scope = (predicted_intent == "OUT_OF_SCOPE") or (predicted_service == "Out-of-Scope")

            # Determine recommended action
            if predicted_intent == "GREETING":
                recommended_action = "Greet user warmly and offer technical assistance on AWS services."
            elif is_out_of_scope:
                recommended_action = "Reject gracefully as out-of-scope; guide user to AWS Cloud services."
            elif predicted_intent == "CLI_SCRIPT_GENERATION":
                recommended_action = "Retrieve CLI syntax documents and format copyable code commands."
            elif predicted_intent == "TROUBLESHOOTING":
                recommended_action = "Retrieve step-by-step diagnostic procedures and error remedies."
            elif predicted_intent == "SECURITY_BEST_PRACTICE":
                recommended_action = "Surface IAM least privilege guidelines and secure configuration policies."
            else:
                recommended_action = "Retrieve architectural guides and structured technical summaries."

            latency_ms = round((time.perf_counter() - start_time) * 1000, 3)

            return {
                "intent": predicted_intent,
                "intent_confidence": round(intent_conf, 4),
                "service": predicted_service,
                "service_confidence": round(service_conf, 4),
                "urgency": predicted_urgency,
                "is_out_of_scope": is_out_of_scope,
                "recommended_action": recommended_action,
                "latency_ms": latency_ms
            }
        except Exception as e:
            logger.error(f"Inference error in IntentClassifier: {e}")
            return self._heuristic_fallback(query, start_time)

    def _heuristic_fallback(self, query: str, start_time: float) -> Dict[str, Any]:
        """Ultra-fast regex/keyword heuristic fallback when ML bundle is unavailable."""
        q = query.lower()
        service = "General AWS"
        intent = "CONCEPTUAL_EXPLANATION"
        urgency = "LOW"
        is_oos = False

        greetings = ["hello", "hi", "hey", "good morning", "good afternoon", "good evening", "how are you", "who are you", "thank", "thanks", "bye", "goodbye"]
        if any(q.startswith(g) or f" {g} " in f" {q} " for g in greetings):
            intent = "GREETING"
            service = "General AWS"
            urgency = "LOW"
        elif "azure" in q or "gcp" in q or "recipe" in q or "quantum" in q:
            is_oos = True
            intent = "OUT_OF_SCOPE"
            service = "Out-of-Scope"
        elif "ec2" in q or "ssh" in q or "publickey" in q:
            service = "Amazon EC2"
        elif "s3" in q or "bucket" in q or "nosuchbucket" in q:
            service = "Amazon S3"
        elif "lambda" in q or "timeout" in q:
            service = "AWS Lambda"
        elif "iam" in q or "policy" in q or "least privilege" in q:
            service = "AWS IAM"

        if not is_oos:
            if "error" in q or "fix" in q or "fail" in q or "timed out" in q or "denied" in q:
                intent = "TROUBLESHOOTING"
                urgency = "HIGH"
            elif "cli" in q or "command" in q or "script" in q or "boto3" in q:
                intent = "CLI_SCRIPT_GENERATION"
            elif "security" in q or "least privilege" in q or "rotate" in q:
                intent = "SECURITY_BEST_PRACTICE"
                urgency = "HIGH"
            elif "how to configure" in q or "setup" in q or "attach" in q:
                intent = "CONFIGURATION_SETUP"

        latency_ms = round((time.perf_counter() - start_time) * 1000, 3)
        return {
            "intent": intent,
            "intent_confidence": 0.85,
            "service": service,
            "service_confidence": 0.85,
            "urgency": urgency,
            "is_out_of_scope": is_oos,
            "recommended_action": "Fallback heuristic routing.",
            "latency_ms": latency_ms
        }

_global_classifier = None

def get_intent_classifier() -> IntentClassifier:
    global _global_classifier
    if _global_classifier is None:
        _global_classifier = IntentClassifier()
    return _global_classifier

