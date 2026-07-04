
import os
import sys
import logging
import asyncio

# Setup logging to stdout with UTF-8 support for Windows
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

logging.basicConfig(level=logging.INFO, stream=sys.stdout)
logger = logging.getLogger(__name__)

# Add CURRENT directory to path (backend/)
sys.path.append(os.getcwd())

from app.agents.langgraph_pipeline import CivicAgentPipeline

async def test():
    print("Initializing pipeline...")
    try:
        pipeline = CivicAgentPipeline()
        user_query = "എനിക്കൊരു വാഹന അപകടം ഉണ്ടായി ഞാൻ എന്ത് ചെയ്യണം"
        print(f"Testing pipeline with query: {user_query}")
        
        # history must be a list of dicts
        history = []
        session_id = f"repro_session_{os.getpid()}"
        
        result = pipeline.run(user_query, history=history, session_id=session_id)
        print("\n\n=== PIPELINE SUCCESS ===")
        print(result)
    except Exception as e:
        print("\n\n=== PIPELINE CRASHED ===")
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test())
