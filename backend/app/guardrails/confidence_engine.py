import logging
from typing import Dict, Any, List
import string

logger = logging.getLogger(__name__)

class ConfidenceEngine:
    """
    Composite Confidence Engine calculating a strict deterministic score for Trust layer.
    """
    def generate_composite_score(
        self,
        retrieval_similarities: List[float],
        final_answer: str,
        citations_found: int,
        prompt_temperature: float,
        generation_token_count: int,
        risk_level: str
    ) -> Dict[str, Any]:
        """
        Calculates a composite confidence score [0.0 - 100.0] derived from vectors, metadata, & output.
        """
        
        # 1. Retrieval Similarity Component (Max 40 points)
        avg_retrieval = (sum(retrieval_similarities) / len(retrieval_similarities)) if retrieval_similarities else 0.0
        # Assume cosine distance scaled 0-1, 1 being perfect match
        retrieval_score = min(avg_retrieval * 40.0, 40.0)
        
        # 2. Citation Density Component (Max 30 points)
        # Expected e.g., 1 citation per major claim
        citation_score = min(citations_found * 15.0, 30.0)
        
        # 3. Model Uncertainty Proxy (Max 30 points)
        # High temperature or extremely high token count (waffling) reduces certainty
        temp_penalty = prompt_temperature * 10.0 # 0.0 gets 0 penalty
        # Token density proxy (say ideal length is ~200 tokens)
        token_entropy_penalty = min(generation_token_count / 1000.0 * 10.0, 10.0) 
        uncertainty_score = max(30.0 - temp_penalty - token_entropy_penalty, 0.0)

        # 4. Risk Penalty (Subtraction)
        risk_penalty = 0.0
        if risk_level == "MODERATE":
            risk_penalty = 15.0
        elif risk_level == "HIGH":
            risk_penalty = 40.0
            
        base_confidence = retrieval_score + citation_score + uncertainty_score
        final_confidence = max(base_confidence - risk_penalty, 0.0)
        
        return {
            "confidence_score": round(final_confidence, 2),
            "breakdown": {
                "retrieval_score": round(retrieval_score, 2),
                "citation_score": round(citation_score, 2),
                "uncertainty_score": round(uncertainty_score, 2),
                "risk_penalty": round(risk_penalty, 2)
            }
        }
        
    def check_escalation(self, composite_result: dict, conflict_detected: bool, risk_level: str) -> bool:
        """Determines if HITL escalation is required."""
        score = composite_result.get("confidence_score", 0.0)
        if score < 60.0:
            return True
        if risk_level == "HIGH":
            return True
        if conflict_detected:
            return True
        return False
