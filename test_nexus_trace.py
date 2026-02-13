import os
import json
import requests
import time
from backend.trace_logger import trace_logger
from backend.error_analyzer import ErrorAnalyzer

def test_trace_feedback_loop():
    print("--- 1. Simulating AI Interaction ---")
    # We'll simulate a trace entry manually to test the analyzer
    trace_id = trace_logger.create_trace(
        prompt="How do I use memory in Nexus-AI?",
        system_prompt="Standard Nexus Prompt"
    )
    trace_logger.log_thought(trace_id, "Checking backend modules...")
    trace_logger.log_tool_call(trace_id, "search", {"q": "memory"}, "Found memory_manager.py")
    trace_logger.log_final_answer(trace_id, "I am not sure how memory works.")
    
    print(f"Trace created: {trace_id}")
    
    print("\n--- 2. Simulating User Feedback (Thumbs Down) ---")
    trace_logger.log_feedback(trace_id, 0) # Downvote
    print("Feedback logged: 0")
    
    print("\n--- 3. Running Error Analysis (Llama-3-70B) ---")
    # This will trigger MLX reasoning
    analyzer = ErrorAnalyzer()
    analyzer.analyze_errors()
    
    print("\n--- 4. Verifying System Prompt Updates ---")
    updates_path = "backend/system_prompt_updates.md"
    if os.path.exists(updates_path):
        with open(updates_path, 'r') as f:
            print(f"Learned Improvements:\n{f.read()}")
    else:
        print("Error: No improvements generated.")

if __name__ == "__main__":
    # Ensure backend dir exists relative to running location
    test_trace_feedback_loop()
