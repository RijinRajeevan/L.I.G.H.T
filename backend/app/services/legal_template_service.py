class LegalTemplateService:
    """
    Phase 6: Deterministic Legal Mode
    Ensures absolute safety for high-risk legal queries.
    - No free reasoning or predictive language
    - Fixed template structures
    - Mandatory jurisdiction & confidence checks
    """
    def __init__(self):
        self.disclaimer = (
            "DISCLAIMER: This is deterministic civic information based on retrieved codes. "
            "It does NOT constitute binding legal advice. Consult a registered advocate."
        )

    def generate_legal_response(self, context: dict, citations: list, confidence: float) -> dict:
        """
        Deterministic formatter. No LLM generative text used here.
        """
        # 1. Mandatory Checks
        jurisdiction = context.get("jurisdiction")
        if not jurisdiction:
            return self._refusal("Ambiguous jurisdiction. Cannot provide legal mapping without a specified state/region.")
            
        if confidence < 0.85:
            return self._refusal(f"Low confidence score ({confidence:.2f}). This query requires manual legal review.")
            
        if not citations:
            return self._refusal("Insufficient data. No validated legal citations found for this query.")

        # 2. Fixed Structure Template
        validated_fields = {
            "jurisdiction": jurisdiction,
            "applicable_sections": citations,
            "mandatory_process": [
                "Draft a formal complaint referencing these specific sections.",
                "Visit the local jurisdictional authority with identity proof.",
                "Seek certified legal counsel before binding agreements."
            ]
        }
        
        return {
            "status": "LEGAL_MODE_SUCCESS",
            "disclaimer": self.disclaimer,
            "safety_enforced": True,
            "validated_content": validated_fields
        }

    def _refusal(self, reason: str) -> dict:
        return {
            "status": "REFUSED_LEGAL_MODE",
            "reason": reason,
            "disclaimer": self.disclaimer
        }
