from ..llm.groq_client import GroqClient
from ..services.vector_store import get_vector_store
from ..utils.json_cleaner import parse_json_safely
import os
import json

class LegalAgent:
    """
    Acts as a 'Service & Legal Agent' for Akshaya Centre activities.
    Covers Revenue, Police, RTO, Passport, etc.
    """
    def __init__(self):
        self.llm = GroqClient()
        self.vector_store = get_vector_store()
        
        # 1. Load Akshaya Services Knowledge Base
        self.akshaya_data = {}
        akshaya_path = "backend/app/data/akshaya_services.json"
        if os.path.exists(akshaya_path):
            with open(akshaya_path, "r", encoding="utf-8") as f:
                self.akshaya_data = json.load(f)

        # 2. Initialize connection to ChromaDB collections
        # Data should be indexed via scripts/index_legal_corpus.py 
        self.ipc_collection = "ipc"
        self.bsa_collection = "bsa"

    def _get_relevant_service(self, query):
        """Match query keywords to Akshaya services"""
        query_lower = query.lower()
        services = self.akshaya_data.get("services", {})
        keywords = self.akshaya_data.get("service_keywords", {})
        
        matched_service = None
        for service_id, tags in keywords.items():
            if any(tag.lower() in query_lower for tag in tags):
                matched_service = services.get(service_id)
                break
        return matched_service

    def analyze(self, query, history=None):
        # 1. Match with Akshaya Service
        service_info = self._get_relevant_service(query)
        
        # 1b. If no service matched CURRENT query, look at history
        if not service_info and history:
            for msg in reversed(history):
                if msg.get('role') == 'user':
                    service_info = self._get_relevant_service(msg.get('text', ''))
                    if service_info:
                        break

        # 2. Retrieve relevant legal codes if needed
        legal_context = ""
        # Only search IPC/BSA if the query seems legal or the matched service is FIR
        is_legal_query = any(k in query.lower() for k in ["stole", "theft", "complaint", "police", "legal", "crime", "cheated", "assault"])
        
        if is_legal_query or (service_info and service_info.get("name") == "Police FIR / Complaint"):
            results = self.vector_store.search(self.ipc_collection, query, top_k=3)
            if results:
                legal_context += "\nRelevant IPC/BNS Sections:\n"
                for res in results:
                    legal_context += f"- Section {res.get('Section', 'N/A')}: {res.get('Description', 'N/A')} (Relevance: {res.get('score', 0):.2f})\n"

        # 3. Format History
        history_str = ""
        if history:
            history_str = "\n".join([f"{m.get('role', 'user')}: {m.get('text', '')}" for m in history if m is not None])

        # 4. Formulate Prompt
        prompt = f"""Role: Govt Assistance Officer Kiosk. 
        CONTEXT: You are helping a citizen with a specific government service.
        MVP SERVICES: Aadhaar, Passport, DL, Caste, Birth, Death.
        
        HISTORY: {history_str[-1000:] if history_str else "New Session"}
        USER INPUT: "{query}"
        
        CURRENT SERVICE (STAY ON THIS): {json.dumps(service_info) if service_info else "General Public Service"}
        LAW (RELEVANT CODES): {legal_context[:500] if legal_context else "None"}
        
        TASK:
        1. If CURRENT SERVICE is an MVP service, collect ALL 'required_info' fields: {service_info.get('required_info') if service_info else 'N/A'}.
        2. Ask ONE question at a time for missing fields. Set status to 'NEEDS_INFO'.
        3. Once ALL fields are collected, set status to 'SUCCESS'.
        4. In 'SUCCESS', include a 'form_data' object with ALL the collected fields mapped to their IDs.
        5. Set 'can_generate_form' to true in 'SUCCESS'.

        Format (Strict JSON):
        {{
            "status": "SUCCESS" | "NEEDS_INFO",
            "package": {{
                "1_problem_summary": "...", "2_recommended_service": "...",
                "3_step_by_step_plan": ["Step 1", "Step 2"], "4_required_documents": ["Doc 1"],
                "5_missing_documents": ["Doc A"], "6_office_to_visit": "...",
                "7_fees_and_timeline": "...", "8_warnings_tips": ["Tip 1"],
                "9_simple_explanation": "..."
            }},
            "questions": ["Next Question"],
            "advice": "Friendly summary.",
            "form_data": {{ "field_id": "value", ... }},
            "can_generate_form": true | false,
            "form_id": "{service_info.get('form_id') if service_info else ''}"
        }}
        Rule: If info is missing for a complete plan, ask 1 question and set NEEDS_INFO.
        """
        
        response_text = self.llm.get_completion(prompt, system_prompt="Helpful human assistant. Output JSON only.")
        
        # Clean and parse to ensure valid JSON
        cleaned_response = parse_json_safely(response_text)
        if cleaned_response and isinstance(cleaned_response, dict):
            # Ensure mandatory fields exist for the coordinator
            if "status" not in cleaned_response:
                cleaned_response["status"] = "SUCCESS"
            
            # HARD OVERRIDE: If there are questions, it MUST be NEEDS_INFO
            if cleaned_response.get("questions") and len(cleaned_response["questions"]) > 0:
                cleaned_response["status"] = "NEEDS_INFO"
                
            return json.dumps(cleaned_response)
        
        # Fallback if parsing fails - create a SUCCESS shell around the text
        fallback_advice = response_text if isinstance(response_text, str) else "The AI service is currently very busy. I'm having trouble processing this right now—please try again after a few seconds."
        
        return json.dumps({
            "status": "SUCCESS",
            "service_name": "Service Assistant",
            "advice": fallback_advice,
            "reasoning": "JSON parsing fallback triggered or AI returned None."
        })

if __name__ == "__main__":
    agent = LegalAgent()
    print(agent.analyze("someone stole my bike"))
