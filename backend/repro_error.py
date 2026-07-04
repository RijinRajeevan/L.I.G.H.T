import sys
import os
sys.path.append(os.getcwd())

from app.orchestration.adk_coordinator import get_adk_coordinator
import json

def test():
    coord = get_adk_coordinator()
    print("Testing analyze('hi')...")
    try:
        result = coord.analyze("hi")
        print("Result:", json.dumps(result, indent=2))
    except Exception as e:
        import traceback
        print("Caught Exception in test script:")
        traceback.print_exc()

if __name__ == "__main__":
    test()
