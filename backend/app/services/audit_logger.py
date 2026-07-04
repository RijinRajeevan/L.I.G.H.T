import logging
from typing import Dict, Any, List
from ..db.database import AsyncSessionLocal
from ..db.models import AuditLog

logger = logging.getLogger(__name__)

class AuditLogger:
    """
    Asynchronous audit logger that writes trace events to the database without blocking.
    """
    @staticmethod
    async def log_execution(
        session_id: str,
        user_query: str,
        retrieved_documents: List[Dict[str, Any]],
        tools_invoked: List[str],
        model_parameters: Dict[str, Any],
        token_usage: int,
        response_latency: float,
        final_answer: str,
        confidence_score: float,
        risk_level: str
    ):
        try:
            async with AsyncSessionLocal() as db:
                log_entry = AuditLog(
                    session_id=session_id,
                    user_query=user_query,
                    retrieved_documents=retrieved_documents,
                    tools_invoked=tools_invoked,
                    model_parameters=model_parameters,
                    token_usage=token_usage,
                    response_latency=response_latency,
                    final_answer=final_answer,
                    confidence_score=confidence_score,
                    risk_level=risk_level
                )
                db.add(log_entry)
                await db.commit()
        except Exception as e:
            # We must never crash the main application if audit logging fails
            logger.error(f"Failed to write to AuditLog DB for session {session_id}: {e}", exc_info=True)
