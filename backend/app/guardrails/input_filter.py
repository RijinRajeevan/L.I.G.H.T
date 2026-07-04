import re

class InputFilter:
    """
    Input Guardrails:
    - Malicious intent detection
    - Prompt injection protection
    - Risk-level tagging
    """
    def __init__(self):
        # Basic mock rules for demonstration
        self.malicious_patterns = [
            r"ignore all previous instructions", 
            r"system prompt", 
            r"you are a developer",
            r"disregard safety",
            r"bypass guardrail"
        ]
        self.risk_keywords = ["bomb", "attack", "hack", "exploit"]

    def validate(self, user_input: str) -> dict:
        text = user_input.lower()
        
        # 1. Prompt Injection Protection
        for pattern in self.malicious_patterns:
            if re.search(pattern, text):
                return {"safe": False, "reason": "Potential prompt injection detected.", "risk_level": "CRITICAL"}
                
        # 2. Malicious Intent Detection
        for keyword in self.risk_keywords:
            if keyword in text:
                return {"safe": False, "reason": f"High risk keyword detected: {keyword}", "risk_level": "HIGH"}
                
        # 3. Risk-level tagging
        risk_level = "LOW"
        if any(w in text for w in ["legal", "sue", "court", "lawyer", "police", "arrest", "fir", "jail"]):
            risk_level = "MODERATE" # Indicates we must use strict legal determinism

        return {"safe": True, "reason": "Input passed security filters.", "risk_level": risk_level}
