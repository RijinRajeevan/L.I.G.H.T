from ..llm.groq_client import GroqClient
from ..utils.json_cleaner import parse_json_safely
import json

class RiskAgent:
    def __init__(self):
        self.llm = GroqClient()
        
    def analyze(self, query, legal_advice=""):
        prompt = f"""You are the Risk Assessment Agent. You are PESSIMISTIC and CAUTIOUS.
        User Situation: "{query}"
        Proposed Legal Advice (if any): "{legal_advice}"
        
        Task:
        1. Identify potential risks for the user (physical, financial, social).
        2. Identify risks of the legal advice (e.g., retaliation, lack of evidence).
        3. Flag if the situation seems to be a trap or fake.
        
        Output Format:
        {{
            "risks": ["Risk 1", "Risk 2"],
            "severity": "High/Medium/Low",
            "concerns": "..."
        }}
        Return ONLY valid JSON.
        """
        
        response_text = self.llm.get_completion(prompt, system_prompt="You are a cynical risk analyst. Output JSON only.", model="llama-3.1-8b-instant")
        
        # Clean and parse to ensure valid JSON
        cleaned_response = parse_json_safely(response_text)
        if cleaned_response:
            return json.dumps(cleaned_response)
            
        return response_text

if __name__ == "__main__":
    agent = RiskAgent()
    print(agent.analyze("I want to sue my neighbor for loud music"))
