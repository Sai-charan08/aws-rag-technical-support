import re
from typing import Optional, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from src.models.solutions_data import AWS_SOLUTIONS
from src.utils.logger import get_logger

logger = get_logger(__name__)

class SolutionModel:
    """Trained Model that maps user requests directly to exact suitable solutions without extraneous text."""

    def __init__(self):
        self.solutions = AWS_SOLUTIONS
        self.queries = [item["query"] for item in self.solutions]
        
        # Build vectorizer on queries + keyword variants
        augmented_texts = []
        for item in self.solutions:
            combined = item["query"] + " " + " ".join(item.get("keywords", []))
            augmented_texts.append(combined)

        self.vectorizer = TfidfVectorizer(ngram_range=(1, 3), lowercase=True, sublinear_tf=True)
        self.matrix = self.vectorizer.fit_transform(augmented_texts)
        logger.info(f"SolutionModel trained and ready with {len(self.solutions)} precise solutions.")

    def get_exact_solution(self, user_query: str, threshold: float = 0.35) -> Optional[str]:
        """Returns exact suitable solution if query matches known technical pattern."""
        if not user_query or not user_query.strip():
            return None

        q_clean = user_query.lower().strip()

        # Direct fast match for exact phrase or keyword list
        for item in self.solutions:
            item_q = item["query"].lower().strip()
            item_kw = [k.lower().strip() for k in item.get("keywords", [])]
            if q_clean == item_q or q_clean in item_kw:
                logger.info(f"Exact keyword match found for '{user_query}' -> '{item['query']}'")
                return item["solution"]

        features = self.vectorizer.transform([user_query])
        similarities = cosine_similarity(features, self.matrix)[0]
        best_idx = similarities.argmax()
        best_score = float(similarities[best_idx])

        if best_score >= threshold:
            logger.info(f"Exact solution match found for '{user_query}' (Score: {best_score:.3f})")
            return self.solutions[best_idx]["solution"]

        return None

_global_solution_model = None

def get_solution_model() -> SolutionModel:
    global _global_solution_model
    if _global_solution_model is None:
        _global_solution_model = SolutionModel()
    return _global_solution_model

