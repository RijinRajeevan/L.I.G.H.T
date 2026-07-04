import logging
import asyncio
from ..agents.langgraph_pipeline import CivicAgentPipeline

logger = logging.getLogger(__name__)

class OrchestratorService:
    """
    Orchestrates agent calls asynchronously using the LangGraph pipeline.
    Ensures all agent_logs are passed through to the frontend NeuralLink.
    """
    def __init__(self):
        self.pipeline = CivicAgentPipeline()

    async def analyze_async(self, user_query: str, history: list = None, session_id: str = "default_session") -> dict:
        """Main analysis workflow — runs pipeline and returns structured output with full agent logs."""
        try:
            logger.info(f"Initiating pipeline analysis for session [{session_id}]...")

            import time
            from .audit_logger import AuditLogger
            from .escalation_service import EscalationService

            start_time = time.time()
            result = await asyncio.to_thread(self.pipeline.run, user_query, history, session_id)
            latency = time.time() - start_time

            # ── Extract pipeline metadata ──────────────────────────────────────
            confidence_score = result.get("confidence_score", 100.0)
            risk_level = result.get("risk_level", "LOW")
            status = result.get("status", "SUCCESS")

            # ── Full agent_logs from pipeline (used by NeuralLink) ─────────────
            # The pipeline builds agent_logs in state["agent_logs"] and the run()
            # method attaches them as result["agent_logs"].
            agent_logs = result.get("agent_logs", [])
            if not agent_logs:
                agent_logs = [{"agent": "Pipeline", "msg": "Graph executed successfully."}]

            # ── DB Audit Log ───────────────────────────────────────────────────
            try:
                await AuditLogger.log_execution(
                    session_id=session_id,
                    user_query=user_query,
                    retrieved_documents=[],
                    tools_invoked=["LangGraph_Pipeline"],
                    model_parameters={"temperature": 0.0, "max_tokens": 1024},
                    token_usage=result.get("token_usage", 0),
                    response_latency=latency,
                    final_answer=str(result.get("advice", "")),
                    confidence_score=confidence_score,
                    risk_level=risk_level
                )
            except Exception as audit_err:
                logger.warning(f"Audit log failed (non-fatal): {audit_err}")

            # ── Route by status ────────────────────────────────────────────────
            if status == "ESCALATED":
                try:
                    await EscalationService.flag_for_review(
                        session_id=session_id,
                        user_query=user_query,
                        confidence_score=confidence_score,
                        risk_flag=risk_level,
                        conflict_detected=False
                    )
                except Exception as esc_err:
                    logger.warning(f"Escalation service failed (non-fatal): {esc_err}")

                return {
                    "status": "ESCALATED",
                    "escalation_required": True,
                    "reason": "This query requires human-in-the-loop review due to low confidence or high risk.",
                    "agent_logs": agent_logs,
                }

            if status in ("REFUSED", "REFUSED_LEGAL_MODE", "FILTERED"):
                # Pull polite message from structured_output.reason first
                structured = result.get("structured_output", {})
                polite_reason = (
                    structured.get("reason")
                    or result.get("refusal_reason")
                    or result.get("reason")
                    or "I'm sorry, I'm unable to assist with that request. For genuine legal queries, contact the NALSA helpline at 15100."
                )
                return {
                    "status": "SUCCESS",  # Render as a normal message, not an error
                    "advice": polite_reason,
                    "sections": [],
                    "agent_logs": agent_logs,
                }

            if status == "NEEDS_INFO":
                questions = result.get("questions", ["Can you provide more details about your situation?"])
                return {
                    "status": "NEEDS_INFO",
                    "questions": questions,
                    "agent_logs": agent_logs,
                    "structured_output": result.get("structured_output", {}),
                }

            # ── SUCCESS: extract advice and sections from structured_output ────
            # The pipeline sets result["advice"] and result["sections"] directly.
            # Fallback to structured_output sub-object for legacy compatibility.
            advice = result.get("advice", "")
            sections = result.get("sections", [])

            # If advice is still empty, check structured_output
            if not advice:
                structured = result.get("structured_output", {})
                advice = structured.get("advice", structured.get("response", ""))
                if not sections:
                    sections = structured.get("sections", [])

            return {
                "status": "SUCCESS",
                "advice": advice,
                "sections": sections,
                "confidence_score": confidence_score,
                "risk_level": risk_level,
                "agent_logs": agent_logs,
                "download_url": result.get("download_url") or result.get("structured_output", {}).get("download_url"),
            }

        except Exception as e:
            logger.error(f"LangGraph Orchestration Error: {e}", exc_info=True)
            return {
                "status": "ERROR",
                "reason": "Internal Orchestration Pipeline Error",
                "agent_logs": [{"agent": "System", "msg": f"Pipeline error: {str(e)}"}],
            }
