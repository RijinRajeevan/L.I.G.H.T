
import os
import sys
import logging
import asyncio
import io

# UTF8 console support
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

logging.basicConfig(level=logging.INFO, stream=sys.stdout)
logger = logging.getLogger(__name__)

# Add CURRENT directory to path
sys.path.append(os.getcwd())

from app.agents.langgraph_pipeline import CivicAgentPipeline
from app.services.audit_logger import AuditLogger

async def test():
    print("Initializing pipeline...")
    pipeline = CivicAgentPipeline()
    user_query = "എനിക്കൊരു വാഹന അപകടം ഉണ്ടായി ഞാൻ എന്ത് ചെയ്യണം"
    session_id = f"repro_session_{os.getpid()}"
    
    print(f"Running pipeline in thread... (Simulating orchestrator)")
    # LangGraph run is sync, but we call it via to_thread in production
    try:
        # Run sync part
        result = await asyncio.to_thread(pipeline.run, user_query, [], session_id)
        print("Pipeline result obtained.")
        
        # Run async part (Audit Logging)
        print("Running AuditLogger...")
        # Simulating the AuditLogger call in orchestrator_service.py
        await AuditLogger.log_execution(
            session_id=session_id,
            user_query=user_query,
            retrieved_documents=[],
            tools_invoked=["Test"],
            model_parameters={},
            token_usage=100,
            response_latency=1.0,
            final_answer=str(result.get("advice", "")),
            confidence_score=1.0,
            risk_level="LOW"
        )
        print("AuditLogger finished.")
        print("\n=== SUCCESS ===")
    except Exception as e:
        print(f"\n=== CRASHED ===\n{e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test())
