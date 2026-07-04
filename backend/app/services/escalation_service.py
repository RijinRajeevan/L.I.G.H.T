import logging
from ..db.database import AsyncSessionLocal
from ..db.models import EscalationQueue

logger = logging.getLogger(__name__)

class EscalationService:
    """
    Handles routing questionable or high-risk queries to a Human-in-the-Loop review queue.
    """
    @staticmethod
    async def flag_for_review(
        session_id: str,
        user_query: str,
        confidence_score: float,
        risk_flag: str,
        conflict_detected: bool = False
    ):
        """
        Inserts a high-risk session into the DB escalation table for an admin to review.
        """
        try:
            async with AsyncSessionLocal() as db:
                queue_entry = EscalationQueue(
                    session_id=session_id,
                    user_query=user_query,
                    confidence_score=confidence_score,
                    risk_flag=risk_flag,
                    conflict_detected=conflict_detected,
                    status="REQUIRES_REVIEW"
                )
                db.add(queue_entry)
                await db.commit()
                logger.warning(f"Session {session_id} flagged for human review (Escalation).")
        except Exception as e:
            logger.error(f"Failed to flag session {session_id} for review: {e}", exc_info=True)
