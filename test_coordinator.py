from backend.app.agents.coordinator import Coordinator
import sys

def test_coordinator():
    print("🚀 Initializing Coordinator...")
    try:
        coord = Coordinator()
        print("✅ Coordinator Initialized.")
    except Exception as e:
        print(f"❌ Failed to initialize: {e}")
        return

    query = "I found a dead body in my backyard with stab wounds."
    print(f"\nmagnifying glass Query: '{query}'")
    
    try:
        result = coord.run_debate(query)
        print("\n--- Result ---")
        print(result)
        
        logs = result.get("logs", [])
        for log in logs:
            print(f"\n[Agent: {log.get('agent')}]")
            print(f"Msg Type: {type(log.get('msg'))}")
            print(f"Msg Content: {str(log.get('msg'))[:100]}...")
            
    except Exception as e:
        print(f"❌ Execution Failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_coordinator()
