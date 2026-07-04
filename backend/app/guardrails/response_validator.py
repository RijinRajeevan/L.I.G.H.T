import json

class ResponseValidator:
    """
    Generation Guardrails:
    - Strict JSON schema enforcement
    - Citation requirement
    - Post-Generation Validation (Reject hallucinated entities)
    """
    def __init__(self):
        pass

    def validate_generation(self, llm_response: str, require_citation: bool = False, require_jurisdiction: bool = False) -> dict:
        """
        Validates that response is proper JSON and meets generation guardrails.
        """
        try:
            data = json.loads(llm_response)
        except Exception:
            # Block completely in STRICT mode (no raw text)
            return {"valid": False, "reason": "Response is not strict JSON schema.", "data": None}

        # 1. Validate Core Schema
        if "status" not in data:
            return {"valid": False, "reason": "Missing required 'status' field in JSON.", "data": None}

        # 2. Check citations if required
        if require_citation:
            if "citations" not in data or not isinstance(data["citations"], list) or len(data["citations"]) == 0:
                return {"valid": False, "reason": "Missing mandatory citations.", "data": None}

        # 3. Check jurisdiction if required
        if require_jurisdiction:
            if "jurisdiction" not in data or not data["jurisdiction"]:
                return {"valid": False, "reason": "Missing mandatory jurisdiction context.", "data": None}

        return {"valid": True, "reason": "Valid response.", "data": data}

    def validate_citations(self, citations: list, valid_source_ids: list):
        """Reject hallucinated entity citations"""
        for cit in citations:
            if cit not in valid_source_ids:
                return False
        return True
