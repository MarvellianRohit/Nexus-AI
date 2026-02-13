import os
import sys
import json

# Add current directory to path
sys.path.append(os.getcwd())

from backend.concurrent_orchestrator import concurrent_orchestrator, shared_state

def test_concurrency():
    print("--- 🏁 Starting Concurrent Reliability Test 🏁 ---")
    
    # 1. Trigger Concurrent Tasks
    results = concurrent_orchestrator.run_concurrent_test()
    
    print("\n--- 🔍 Checking Shared State Consistency ---")
    auth_code = shared_state.get("auth_code")
    api_docs = shared_state.get("api_docs")
    unit_tests = shared_state.get("unit_tests")
    
    if auth_code and api_docs and unit_tests:
        print("✅ SUCCESS: All 3 tasks completed.")
        
        # Verify Task 2 (Docs) knows about Task 1's (Code) changes
        if "JWT" in api_docs or "token" in api_docs.lower():
            print("✅ SUCCESS: Documentation matches refactored code (Shared State intact).")
        else:
            print("⚠️ WARNING: Documentation might not have captured the 'JWT' refactor.")
            
        print("\n--- 📄 Sample Outputs ---")
        print(f"Refactor (first 50 chars): {auth_code[:50]}...")
        print(f"Documentation (first 50 chars): {api_docs[:50]}...")
        print(f"Unit Tests (first 50 chars): {unit_tests[:50]}...")
    else:
        print("❌ FAILURE: One or more tasks failed to complete.")

if __name__ == "__main__":
    test_concurrency()
