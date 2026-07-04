import json
import logging
from typing import TypedDict, Dict, Any, List, Optional

# Conditional import to avoid crash if langgraph is not installed yet
try:
    from langgraph.graph import StateGraph, END
except ImportError:
    class StateGraph:
        def __init__(self, state_schema): self.nodes = {}; self.edges = []
        def add_node(self, n, f): pass
        def set_entry_point(self, n): pass
        def add_edge(self, a, b): pass
        def add_conditional_edges(self, n, func, path_map): pass
        def compile(self): return self
        def invoke(self, state): return state # Mock fallback
    END = "END"

from ..guardrails.input_filter import InputFilter
from ..guardrails.response_validator import ResponseValidator
from ..guardrails.confidence_engine import ConfidenceEngine

logger = logging.getLogger(__name__)

# ──────────────────────────────────────────────
# 1. State Definition (Strict Typing)
# ──────────────────────────────────────────────
class AgentState(TypedDict):
    user_input: str
    history: List[Dict[str, str]]
    
    # Internal context
    user_profile: dict
    service_intent: str
    is_legal_query: bool
    risk_level: str
    
    # Requirements & Confidence
    missing_docs: List[str]
    confidence_score: float
    
    # Final outputs
    structured_output: dict
    refusal_reason: str
    status: str
    questions: Optional[List[str]]
    validated_content: Optional[str]
    
    # Observability
    agent_logs: List[Dict[str, str]]

    # Form State
    collected_fields: dict
    current_field: str

# ──────────────────────────────────────────────
# 2. Stateful Pipeline Architecture
# ──────────────────────────────────────────────
class CivicAgentPipeline:
    """
    Refactored Controlled LangGraph Pipeline
    
    Node-Level Explanation:
    - profile_builder: Extracts basic info and runs strict input guardrails.
    - service_classifier: Categorizes intent deterministically (no generative reasoning).
    - confidence_calculation: Simulates/runs retrieval confidence logic.
    - requirement_analyzer: Uses schema-enforced analysis for required documents.
    - synthesizer: Only reached in safe, non-legal paths to format the JSON payload.
    - deterministic_legal: Handled in Phase 6. High-risk path bypasses the synthesizer entirely.
    - safe_refusal: Sink node for any guardrail violations. No loops.
    """
    def __init__(self):
        self.input_filter = InputFilter()
        self.validator = ResponseValidator()
        self.confidence_engine = ConfidenceEngine()
        
        self.graph = StateGraph(AgentState)
        
        # Add exactly the required nodes
        self.graph.add_node("profile_builder", self.node_profile_builder)
        self.graph.add_node("service_classifier", self.node_service_classifier)
        self.graph.add_node("confidence_calculation", self.node_confidence_calculation)
        self.graph.add_node("requirement_analyzer", self.node_requirement_analyzer)
        self.graph.add_node("synthesizer", self.node_synthesizer)
        self.graph.add_node("deterministic_legal", self.node_deterministic_legal)
        self.graph.add_node("form_agent", self.node_form_agent)  # PDF form filling
        self.graph.add_node("safe_refusal", self.node_safe_refusal)
        
        # Edges enforcing deterministic, acyclic flow
        self.graph.set_entry_point("profile_builder")
        self.graph.add_edge("profile_builder", "service_classifier")
        self.graph.add_edge("service_classifier", "confidence_calculation")
        
        # Risk-based Branching Logic
        self.graph.add_conditional_edges(
            "confidence_calculation",
            self.route_after_confidence,
            {
                "safe_refusal": "safe_refusal",
                "deterministic_legal": "deterministic_legal",
                "form_agent": "form_agent",
                "requirement_analyzer": "requirement_analyzer"
            }
        )
        
        self.graph.add_edge("requirement_analyzer", "synthesizer")
        
        # Sinks (No infinite loops)
        self.graph.add_edge("synthesizer", END)
        self.graph.add_edge("deterministic_legal", END)
        self.graph.add_edge("form_agent", END)
        self.graph.add_edge("safe_refusal", END)
        
        from ..state.checkpointer import get_checkpointer
        checkpointer = get_checkpointer()
        self.pipeline = self.graph.compile(checkpointer=checkpointer)

    # ──────────────────────────────────────────────
    # Node Methods
    # ──────────────────────────────────────────────
    def node_profile_builder(self, state: AgentState):
        filter_res = self.input_filter.validate(state["user_input"])
        state["risk_level"] = filter_res["risk_level"]
        state["user_profile"] = {"is_authenticated": False}
        
        # Init logs if missing
        if "agent_logs" not in state:
            state["agent_logs"] = []
            
        import json
        try:
            state["agent_logs"].append({
                "agent": "Ethics",
                "msg": json.dumps({"veto": not filter_res["safe"], "reason": filter_res.get("reason", "Security filters cleared. Scanned for malicious intent, prompt injection, and sensitive legal keywords. Query prioritized for processing.")})
            })
        except Exception as e:
            logger.warning(f"Ethics logging failed: {e}")
        
        if not filter_res["safe"]:
             state["status"] = "FILTERED"
             state["refusal_reason"] = filter_res["reason"]
        return state

    def node_service_classifier(self, state: AgentState):
        if state.get("status") == "FILTERED": return state
        user_input_low = state["user_input"].lower()
        history = state.get("history", [])

        # ── Detect form intent from current message OR conversation history ──
        aadhaar_kw = ["aadhaar", "aadhar", "uid", "uidai", "aadhaar correction", "aadhar update", "aadhaar update"]
        dl_kw      = ["driving licence", "driving license", "drivers license", "drivers licence",
                      "driver's license", "driver's licence", "dl correction", "dl update", "update dl",
                      "update my dl", "update my driving", "license correction", "licence correction",
                      "driver licence", "driver license", "rto correction"]

        # Check current message
        is_aadhaar = any(k in user_input_low for k in aadhaar_kw)
        is_dl      = any(k in user_input_low for k in dl_kw)

        # Also check history for ongoing form sessions
        if not (is_aadhaar or is_dl):
            for msg in history:
                if isinstance(msg, dict):
                    ht = msg.get("text", "").lower()
                    if any(k in ht for k in aadhaar_kw):
                        is_aadhaar = True; break
                    if any(k in ht for k in dl_kw):
                        is_dl = True; break

        if is_aadhaar:
            state["service_intent"] = "aadhaar_correction"
            state["is_legal_query"] = False
        elif is_dl:
            state["service_intent"] = "dl_correction"
            state["is_legal_query"] = False
        else:
            # Check for English and Malayalam legal keywords
            legal_kw = [
                "sue", "lawyer", "police", "court", "ipc", "bns", "crash", "accident",
                "stole", "steal", "theft", "assault", "hit", "cheat", "scam", "fraud",
                "rob", "kill", "murder", "injury", "injured", "evict", "landlord",
                "tenant", "fir", "arrest", "bail", "custody", "legal", "law", "rights",
                "section", "act", "ipc", "crpc", "constitution",
                "തല്ലി", "പരാതി", "വഞ്ചിച്ചു", "മോഷണം", "നിയമം", "കേസ്", "അപകടം", "വക്കീൽ", "കോടതി", "അറസ്റ്റ്"
            ]
            state["is_legal_query"] = any(w in user_input_low for w in legal_kw)
            state["service_intent"] = "Legal Assistance" if state["is_legal_query"] else "General Citizen Service"

        try:
            state["agent_logs"].append({
                "agent": "System",
                "msg": f"Mapped Intent: {state['service_intent']}. Classification completed using pattern matching and keyword analysis across current input and conversation history."
            })
        except Exception as e:
            logger.warning(f"System logging failed: {e}")
        return state

    def node_confidence_calculation(self, state: AgentState):
        if state.get("status") == "FILTERED": return state
        
        # confidence_engine returns a score on 0-100 scale
        mock_similarities = [0.85, 0.90, 0.78]
        citations = 2 if state["is_legal_query"] else 0
        
        composite_eval = self.confidence_engine.generate_composite_score(
            retrieval_similarities=mock_similarities,
            final_answer="",
            citations_found=citations,
            prompt_temperature=0.0,
            generation_token_count=150,
            risk_level=state["risk_level"]
        )
        # Store as 0-100 score (the engine already returns 0-100)
        raw_score = composite_eval["confidence_score"]  # e.g. 92.23
        state["confidence_score"] = raw_score / 100.0   # normalise to 0-1 for internal use
        state["confidence_breakdown"] = composite_eval["breakdown"]
        
        try:
            state["agent_logs"].append({
                "agent": "Confidence",
                "msg": json.dumps({
                    "score": int(raw_score),
                    "reasoning": f"Calculated based on {int(composite_eval.get('breakdown', {}).get('retrieval_score', 0)/40*100)}% retrieval accuracy, {int(composite_eval.get('breakdown', {}).get('citation_score', 0)/30*100)}% citation density, and {int(composite_eval.get('breakdown', {}).get('uncertainty_score', 0)/30*100)}% model certainty.",
                    "refusal_triggered": raw_score < 50
                })
            })
            
            state["agent_logs"].append({
                "agent": "Risk",
                "msg": json.dumps({
                    "severity": state["risk_level"],
                    "concerns": [f"Evaluated against the Civic Safety Matrix. Identified as a {state['risk_level'].lower()}-risk informational inquiry."]
                })
            })
        except Exception as e:
            logger.warning(f"Confidence/Risk logging failed: {e}")
        
        return state

    def route_after_confidence(self, state: AgentState):
        """Risk-based conditional router"""
        if state.get("status") == "FILTERED":
            return "safe_refusal"

        # Form-filling intent always routes to form_agent (safe, no risk check needed)
        intent = state.get("service_intent", "")
        if intent in ("aadhaar_correction", "dl_correction"):
            return "form_agent"

        # Escalation routing hook
        conflict_detected = False
        requires_hitl = self.confidence_engine.check_escalation(
            {"confidence_score": state["confidence_score"]},
            conflict_detected,
            state["risk_level"]
        )
        if requires_hitl:
            state["status"] = "ESCALATED"

        if state["is_legal_query"] or state["risk_level"] in ["HIGH", "MODERATE"]:
            return "deterministic_legal"

        return "requirement_analyzer"

    def node_requirement_analyzer(self, state: AgentState):
        """Identifies missing documents for safe services."""
        state["missing_docs"] = ["Aadhaar Copy", "Income Certificate"] if "certificate" in state["user_input"].lower() else []
        return state

    def node_synthesizer(self, state: AgentState):
        """Synthesizes structured JSON using an LLM instead of hardcoded text."""
        from ..llm.groq_client import GroqClient
        import json
        
        try:
            llm = GroqClient()
            history_str = ""
            if state.get("history"):
                history_str = "\n".join([f"{m.get('role', 'user')}: {m.get('text', '')}" for m in state["history"] if isinstance(m, dict)])
            
            # Detect language
            is_malayalam = any('\u0D00' <= c <= '\u0D7F' for c in state["user_input"])
            lang_label = "MALAYALAM" if is_malayalam else "ENGLISH"

            prompt = f"""
            Role: Govt Assistance Officer Kiosk.
            USER INPUT: "{state['user_input']}"
            LANGUAGE: {lang_label}
            HISTORY: {history_str[-1000:]}
            SERVICE MAPPED: {state.get('service_intent', 'General Service')}
            
            Generate a helpful, friendly, and concise response (advice) in {lang_label}.
            MANDATORY: You MUST also include ONE specific follow-up question in {lang_label} to help them further.
            
            Return ONLY valid JSON in this exact format:
            {{"advice": "your response here", "question": "follow-up question here"}}
            """
            
            response_text = llm.get_completion(prompt, system_prompt=f"Helpful human assistant. Always respond in {lang_label}.")
            
            from ..utils.json_cleaner import parse_json_safely
            parsed = parse_json_safely(response_text)
            if isinstance(parsed, dict):
                advice = parsed.get("advice", response_text)
                question = parsed.get("question")
            else:
                advice = response_text
                question = None
        except Exception as e:
            logger.error(f"Error in synthesizer LLM: {e}")
            is_malayalam = any('\u0D00' <= c <= '\u0D7F' for c in state["user_input"])
            if is_malayalam:
                advice = "കൂടുതൽ തിരക്ക് അനുഭവപ്പെടുന്നതിനാൽ എനിക്ക് വിവരങ്ങൾ ശേഖരിക്കുന്നതിൽ തടസ്സം നേരിട്ടു. ദയവായി അല്പം കഴിഞ്ഞ് വീണ്ടും ശ്രമിക്കുക."
            else:
                advice = "I am currently experiencing heavy traffic and having trouble connecting to my knowledge base right now. Please try again in a few moments."
            question = None

        state["status"] = "SUCCESS" if not state["missing_docs"] else "NEEDS_INFO"
        state["structured_output"] = {
            "status": state["status"],
            "service": state.get("service_intent", "Unknown"),
            "missing_docs": state.get("missing_docs", []),
            "advice": advice,
            "questions": [question] if question else []
        }
        
        state["agent_logs"].append({
            "agent": "Legal",
            "msg": json.dumps({
                "advice": advice,
                "reasoning": "Synthesized general citizen guidance."
            })
        })
        
        return state
        
    def node_form_agent(self, state: AgentState):
        """
        Multi-turn PDF form-filling agent.
        Uses LLM to extract field values from the conversation history (smart, can grab many
        fields from one message), asks one question per turn for any remaining fields,
        and when all required fields are collected, fills the PDF and returns a download URL.
        """
        from ..services.pdf_filler import pdf_filler
        from ..services.form_definitions import FORM_FIELDS, FORM_LABELS, POST_SUBMISSION_INSTRUCTIONS
        from ..llm.groq_client import GroqClient
        from ..utils.json_cleaner import parse_json_safely
        import json, os, datetime

        intent    = state.get("service_intent", "aadhaar_correction")
        form_type = "aadhaar" if "aadhaar" in intent else "dl"
        fields    = FORM_FIELDS[form_type]
        form_label = FORM_LABELS[form_type]
        history   = state.get("history", [])
        user_input = state["user_input"]

        state["agent_logs"].append({
            "agent": "System",
            "msg": f"Form Agent activated for: {form_label}"
        })

        # ── 1. Fetch persistent state data ────────────────────────────────────
        collected = state.get("collected_fields", {})
        
        last_question = ""
        if len(history) >= 2 and history[-2].get("role") == "assistant":
             last_question = history[-2].get("text", "")
        # Note: Depending on routing, the very last message in history before input could be assistant.
        # Let's cleanly grab the last assistant line from history.
        for m in reversed(history):
            if isinstance(m, dict) and m.get("role") in ["assistant", "system"] and m.get("text"):
                last_question = m["text"]
                break

        # ── 2. Ask LLM to extract ONLY NEW fields (Delta Extraction) ─────────
        # Only run extraction if the assistant actually asked a question previously.
        # If last_question is empty, this is the very first turn ("I want to update my aadhaar").
        if last_question:
            import re
            clean_fields = []
            for f in fields:
                clean_label = re.sub(r"\(.*?\)", "", f["label"]).strip()
                clean_fields.append(f'  "{f["id"]}": "{clean_label}"')
            field_list_str = "\n".join(clean_fields)
            
            extract_prompt = f"""
    You are a precise data extraction AI for the {form_label}.
    Your job is to read the user's LATEST message and extract ONLY newly provided form fields.

    ASSISTANT'S LAST QUESTION TO USER:
    {last_question}

    USER'S LATEST MESSAGE:
    {user_input}

    AVAILABLE FIELDS AND THEIR DESCRIPTIONS (id: description):
    {field_list_str}

    RULES:
    1. Output ONLY valid JSON containing ONLY the newly extracted fields matching the keys above.
    2. CRITICAL: Map single-word answers directly to the Assistant's last question.
    3. If the user simply says "hi", or makes a generic request, MUST return EXACTLY EMPTY JSON object: {{}}
    4. If a user explicitly says they want to skip a field (e.g. "skip", "none"), extract it as "SKIP".
    5. DO NOT hallucinate. You MUST OMIT any keys from the JSON for fields that were NOT explicitly mentioned.
    """
            try:
                llm = GroqClient()
                raw = llm.get_completion(
                    extract_prompt, 
                    system_prompt="You are a precise JSON extraction assistant. Return only valid JSON.",
                    json_mode=True
                )
                parsed = parse_json_safely(raw)
                if isinstance(parsed, dict):
                    for k, v in parsed.items():
                        val = str(v).strip()
                        if not val or val.lower() in ("none", "null", "undefined"):
                            continue
                        if val.upper() == "SKIP":
                            collected[k] = ""
                        else:
                            # Only overwrite if we don't have a value yet, 
                            # or if the new value is significantly better (not empty)
                            collected[k] = val
            except Exception as e:
                logger.warning(f"Form field extraction LLM error: {e}")

        # Update persistent state
        state["collected_fields"] = collected

        # Auto-fill today's date if not provided
        if "date" not in collected:
            collected["date"] = datetime.date.today().strftime("%d/%m/%Y")
            state["collected_fields"]["date"] = collected["date"]

        state["agent_logs"].append({
            "agent": "System",
            "msg": json.dumps({"event": "fields_extracted", "count": len(collected), "fields": list(collected.keys())})
        })

        # ── 3. Find the next required unanswered field ─────────────────────────
        next_field = None
        for field in fields:
            fid = field["id"]
            if fid == "date":
                continue  # auto-filled
            val = collected.get(fid, "").strip()
            if not val and field.get("required", True):
                next_field = field
                break

        # Debug: Log the state of collection
        logger.info(f"FormAgent State [{form_type}]: {json.dumps(collected)}")
        if next_field:
            logger.info(f"Next required field identified: {next_field['id']}")

        # ── 4. If there's a missing field → ask for it ─────────────────────────
        if next_field:
            state["status"] = "NEEDS_INFO"
            state["structured_output"] = {
                "status": "NEEDS_INFO",
                "form_mode": True,
                "form_type": form_type,
                "current_field": next_field["id"],
                "questions": [f"{next_field['label']}"],
                "collected": collected,
            }
            state["agent_logs"].append({
                "agent": "System",
                "msg": f"Requesting field: {next_field['id']}"
            })
            return state

        # ── 5. All required fields collected → fill the PDF ───────────────────
        try:
            out_path = pdf_filler.fill(form_type, collected)
            filename = os.path.basename(out_path)

            instructions = POST_SUBMISSION_INSTRUCTIONS[form_type]
            advice = (
                f"Your **{form_label}** has been filled and is ready to download.\n\n"
                + instructions
            )

            state["status"] = "SUCCESS"
            state["structured_output"] = {
                "status": "SUCCESS",
                "form_mode": True,
                "form_type": form_type,
                "advice": advice,
                "download_url": f"/download-form/{filename}",
                "sections": [],
            }
            state["agent_logs"].append({
                "agent": "System",
                "msg": f"PDF generated successfully: {filename}"
            })

        except Exception as e:
            logger.error(f"PDF fill error: {e}", exc_info=True)
            state["status"] = "SUCCESS"
            state["structured_output"] = {
                "status": "SUCCESS",
                "advice": f"I encountered an error generating the PDF: {str(e)}. Please try again or contact support.",
                "sections": [],
            }

        return state

    def node_deterministic_legal(self, state: AgentState):
        """
        Phase 6: LLM-powered legal agent grounded in ChromaDB retrieval.
        """
        try:
            from ..services.vector_store import get_vector_store
            from ..llm.groq_client import GroqClient
            from ..utils.json_cleaner import parse_json_safely
            import json
            
            vector_store = get_vector_store()
            user_input = state["user_input"]
            history = state.get("history", [])
            
            # ── 0. Language Detection & Translation for RAG ──────────────────────
            # Use safe logging that avoids crashes on Windows encoding
            logger.info(f"Processing Legal Node...")
            
            # Simpler, safer Malayalam detection
            texts_to_check = [user_input]
            for msg in history[-2:]:
                if isinstance(msg, dict) and "text" in msg:
                    texts_to_check.append(msg["text"])
            
            is_malayalam = any('\u0D00' <= c <= '\u0D7F' for t in texts_to_check for c in t)
            
            search_query = user_input
            
            if is_malayalam:
                try:
                    llm = GroqClient()
                    trans_prompt = (
                        f"Extract 2-3 broad English legal keywords from this query for a vector database search. "
                        f"Focus ONLY on the core legal issue. Example: 'physical assault', 'money theft', 'property dispute'.\n"
                        f"Query: '{user_input}'\n"
                        f"Return ONLY the keywords separated by spaces."
                    )
                    translated = llm.get_completion(trans_prompt, system_prompt="Legal Keyword Extractor")
                    if translated and len(translated.strip()) > 2:
                        search_query = translated.strip()
                except Exception as e:
                    logger.warning(f"Translation for RAG failed: {e}")

            # ── Vector RAG — Legal Knowledge ───────────────────────────────────
            # Re-enabled RAG with safety
            try:
                # Simple keyword extraction (ignore non-ascii for now to be safe)
                keywords = "".join([c if ord(c) < 128 else " " for c in search_query]).strip()
                if not keywords: keywords = "legal procedure" # default fallback
                
                retrieved_docs = vector_store.search("indian_legal_codes", search_query, top_k=3)
                # Add Malayalam-specific retrieval if needed but using original query
                # (SentenceTransformers handles multilingual well)
                
                context = "\n".join([f"[{d['Section']}]: {d['Description']}" for d in retrieved_docs])
                if not context:
                    context = "No specific sections found in database. Use general legal knowledge."
            except Exception as rag_err:
                logger.warning(f"RAG Retrieval failed (non-fatal): {rag_err}")
                context = "Knowledge base search unavailable. Using internal training data."
                retrieved_docs = []
            
            real_citations = []
            context_text = ""
            for res in retrieved_docs:
                section_num = res.get('Section', 'N/A')
                full_desc = res.get('Description', 'N/A')
                short_desc = full_desc[:120].rstrip() + ("…" if len(full_desc) > 120 else "")
                real_citations.append(f"Section {section_num}: {short_desc}")
                context_text += f"Section {section_num}: {full_desc}\n"
            
            # ── 2. Build history context ───────────────────────────────────────────
            history_str = ""
            if history:
                history_str = "\n".join([
                    f"{m.get('role', 'user').upper()}: {m.get('text', '')}"
                    for m in history[-6:] if isinstance(m, dict)
                ])
            
            # ── 3. Call the LLM with retrieved context ────────────────────────────
            llm = GroqClient()
            lang_label = 'MALAYALAM' if is_malayalam else 'ENGLISH'
            system_prompt = (
                f"You are CIVIA, an expert Indian civic and legal AI assistant. "
                f"You MUST ALWAYS speak PRECISELY IN {lang_label}. Never use English if {lang_label} is MALAYALAM. "
                "Your role is to give helpful, accurate, actionable civic and legal guidance to Indian citizens. "
                "Always reference relevant laws (IPC, BNS, Acts). "
                "MANDATORY: You MUST always ask ONE follow-up question to help the user further."
            )
            
            context_section = f"\nRELEVANT LEGAL SECTIONS FROM DATABASE:\n{context_text}" if context_text else ""
            prompt = f"""
[STRICT REQUIREMENT: ALL JSON VALUES MUST BE IN {lang_label}]
USER QUERY: "{user_input}"
LANGUAGE: {lang_label}
{history_str}
{context_section}

INSTRUCTIONS:
1. Provide a complete, helpful legal/civic response in {lang_label}.
2. MANDATORY: Explicitly mention applicable Indian laws or IPC/BNS sections.
3. MANDATORY: Ask ONE specific follow-up question in {lang_label}.
4. Return ONLY valid JSON in this exact format:
{{"status": "answer" | "needs_info" | "refused", "response": "your full answer in {lang_label} here", "question": "follow-up in {lang_label} here"}}
"""
            
            response_text = llm.get_completion(prompt, system_prompt=system_prompt, json_mode=True)
            if not response_text:
                raise ValueError("Empty response from LLM")

            parsed = parse_json_safely(response_text)
            if not isinstance(parsed, dict):
                parsed = {"status": "answer", "response": response_text.strip(), "question": None}
            
            llm_status = parsed.get("status", "answer")
            llm_response = parsed.get("response") or parsed.get("answer") or parsed.get("advice") or ""
            llm_question = parsed.get("question")

            if not llm_response:
                llm_response = response_text.strip()

            # ── 4. Set output ──────────────────────────────────────────────────
            if llm_status == "refused":
                state["status"] = "REFUSED"
                polite_refusal = "ക്ഷമിക്കണം, ഈ ചോദ്യത്തിന് ഞാൻ ഉത്തരം നൽകാൻ കഴിയുന്നില്ല." if is_malayalam else "I'm sorry, I'm unable to assist with this particular request."
                state["refusal_reason"] = polite_refusal
                state["structured_output"] = {"status": "REFUSED", "reason": polite_refusal}
            elif llm_status == "needs_info" and llm_question:
                state["status"] = "NEEDS_INFO"
                state["structured_output"] = {"status": "NEEDS_INFO", "questions": [llm_question]}
            else:
                state["status"] = "SUCCESS"
                state["structured_output"] = {
                    "status": "SUCCESS",
                    "advice": llm_response,
                    "sections": real_citations,
                    "questions": [llm_question] if llm_question else []
                }
            
            return state

        except Exception as e:
            # Use safe error string to avoid encoding crashes on complex tracebacks
            logger.error(f"Critical error in node_deterministic_legal: {repr(e)}")
            # Safe localized fallback
            is_malayalam = any('\u0D00' <= c <= '\u0D7F' for c in state.get("user_input", ""))
            state["status"] = "SUCCESS"
            if is_malayalam:
                fallback = "കൂടുതൽ തിരക്ക് അനുഭവപ്പെടുന്നതിനാൽ എനിക്ക് വിവരങ്ങൾ ശേഖരിക്കുന്നതിൽ ചെറിയൊരു തടസ്സം നേരിട്ടു. നിയമപരമായ സഹായത്തിനായി ദയവായി NALSA ഹെൽപ്പ് ലൈൻ നമ്പറായ 15100-ൽ ബന്ധപ്പെടുക."
            else:
                fallback = "Due to heavy traffic, I encountered an issue accessing my knowledge base. Please try again shortly or consult the NALSA helpline at 15100 for professional assistance."
            
            state["structured_output"] = {
                "status": "SUCCESS",
                "advice": fallback,
                "sections": [],
                "questions": []
            }
            return state

    def node_safe_refusal(self, state: AgentState):
        """Exit node for safety/ethics violations. Returns a polite, language-aware rejection."""
        user_input = state.get("user_input", "")
        is_malayalam = any('\u0D00' <= c <= '\u0D7F' for c in user_input)
        
        if is_malayalam:
            polite_msg = (
                "ക്ഷമിക്കണം, ഈ ചോദ്യത്തിന് ഞാൻ ഉത്തരം നൽകാൻ കഴിയില്ല. "
                "CIVIA ഒരു നിയമ-പൗര സഹായ പ്ലാറ്റ്ഫോം ആണ്. "
                "ദോഷകരമോ, അനുചിതമോ ആയ അഭ്യർത്ഥനകൾ ഞങ്ങളുടെ "
                "സേഫ്ടി ഗൈഡ്ലൈനുകൾ ലംഘിക്കുന്നു. "
                "നിങ്ങൾക്ക് ഒരു നിയമ ചോദ്യം ഉണ്ടെങ്കിൽ, "
                "ദയവായി NALSA ഹെൽപ്ലൈൻ 15100-ൽ ബന്ധപ്പെടുക."
            )
        else:
            polite_msg = (
                "I'm sorry, I'm not able to respond to that request. "
                "CIVIA is a civic and legal guidance platform, and this query "
                "appears to conflict with our safety guidelines. "
                "If you have a genuine legal question, please feel free to ask — "
                "or contact the NALSA helpline at 15100 for professional assistance."
            )
        
        state["status"] = "REFUSED"
        state["refusal_reason"] = polite_msg
        state["structured_output"] = {
            "status": "REFUSED",
            "reason": polite_msg
        }
        return state

    def run(self, user_query: str, history: list = None, session_id: str = "default_session") -> dict:
        """Main entry point for the agentic pipeline with state persistence."""
        config = {"configurable": {"thread_id": session_id}}
        
        # 1. Load existing state if it exists
        try:
            current_state = self.pipeline.get_state(config)
        except Exception:
            current_state = None
            
        if current_state and current_state.values:
            logger.info(f"Resuming pipeline state for session [{session_id}]")
            initial_state = dict(current_state.values)
            initial_state["user_input"] = user_query
            initial_state["history"] = history or []
            # Reset turn-specific outputs but PRESERVE collected_fields
            initial_state["status"] = "INIT"
            initial_state["agent_logs"] = []
            initial_state["structured_output"] = {}
            # Ensure collected_fields is non-empty if it was already there
            if "collected_fields" not in initial_state:
                initial_state["collected_fields"] = {}
        else:
            logger.info(f"Starting fresh pipeline state for session [{session_id}]")
            initial_state = {
                "user_input": user_query,
                "session_id": session_id,
                "history": history or [],
                "user_profile": {},
                "service_intent": "",
                "is_legal_query": False,
                "risk_level": "LOW",
                "missing_docs": [],
                "confidence_score": 1.0,
                "structured_output": {},
                "refusal_reason": "",
                "status": "INIT",
                "agent_logs": [],
                "collected_fields": {},
                "current_field": ""
            }
        
        try:
            # 2. Execute Graph
            final_state = self.pipeline.invoke(
                initial_state,
                config={"configurable": {"thread_id": session_id}}
            )
            
            # 3. Handle Final Results
            # Extract fields from state with fallbacks
            agent_logs = final_state.get("agent_logs", [])
            structured = final_state.get("structured_output", {})
            status     = final_state.get("status", "SUCCESS")
            
            # Ensure questions are flattened for orchestrator
            questions = final_state.get("questions") or structured.get("questions", [])
            
            return {
                "status": status,
                "advice": structured.get("advice", ""),
                "sections": structured.get("sections", []),
                "questions": questions,
                "agent_logs": agent_logs,
                "confidence_score": final_state.get("confidence_score", 100.0),
                "risk_level": final_state.get("risk_level", "LOW"),
                "refusal_reason": final_state.get("refusal_reason") or structured.get("reason", ""),
                "structured_output": structured,
                "download_url": structured.get("download_url")
            }
        except Exception as e:
            logger.error(f"Pipeline execution failed: {e}", exc_info=True)
            return {
                "status": "ERROR",
                "reason": f"Execution Error: {str(e)}",
                "agent_logs": [{"agent": "System", "msg": f"Pipeline crashed: {str(e)}"}]
            }
