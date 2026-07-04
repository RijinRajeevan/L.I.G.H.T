from ..llm.groq_client import GroqClient
import json
import os

class QuestioningAgent:
    """
    Evaluates if enough information is gathered for a specific service.
    Returns follow-up questions if data is missing.
    """
    def __init__(self):
        self.llm = GroqClient()
        self.akshaya_data = {}
        akshaya_path = "backend/app/data/akshaya_services.json"
        if os.path.exists(akshaya_path):
            with open(akshaya_path, "r", encoding="utf-8") as f:
                self.akshaya_data = json.load(f)

    def evaluate(self, query, history, matched_service_name=None):
        """
        Evaluate if we have enough info.
        Returns: {
            "needs_more_info": bool,
            "questions": [str],
            "confidence_score": int
        }
        """
        services = self.akshaya_data.get("services", {})
        service_info = None
        
        # If service was already matched by the LegalAgent, use it.
        # Otherwise, try to find it again.
        if matched_service_name:
            for s_id, s_data in services.items():
                if s_data.get("name") == matched_service_name:
                    service_info = s_data
                    break
        
        if not service_info:
            # Fallback: Let LLM identify the service first if not provided
            service_info = self._identify_service_via_llm(query, history)

        if not service_info:
            # Generic query, no specific service info needed yet
            return {"needs_more_info": False, "questions": [], "confidence_score": 100}

        required_fields = service_info.get("required_info", [])
        
        prompt = f"""You are a data validation agent for a government service kiosk.
        Service: {service_info.get('name')}
        Required Information to give a definitive answer: {", ".join(required_fields)}
        
        Current User Input: "{query}"
        Previous Conversation History: {json.dumps(history[-4:] if history else [])}
        
        TASK:
        1. Check which required fields are missing.
        2. If critical info is missing, generate 1-3 polite follow-up questions.
        3. If enough info is present to give a general guide, set needs_more_info to false.
        
        Return ONLY valid JSON.
        
        Example Output:
        {{
            "needs_more_info": true,
            "questions": ["May I know your approximate annual income?", "What is the purpose of this certificate?"],
            "gathered_info": {{"applicant_name": "Rohan"}},
            "confidence_score": 40
        }}
        """
        
        response = self.llm.get_completion(prompt, system_prompt="You are a strict validation agent. Output JSON only.")
        try:
            return json.loads(response)
        except:
            return {"needs_more_info": False, "questions": [], "confidence_score": 50}

    def _identify_service_via_llm(self, query, history):
        # Implementation of identification logic if needed
        # For now, we trust the orchestration to pass the matched service name
        return None
