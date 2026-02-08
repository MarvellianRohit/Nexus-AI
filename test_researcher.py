import os
import sys

# Add current directory to path
sys.path.append(os.getcwd())

try:
    print("Testing import...")
    from backend.researcher.agent import run_researcher
    print("Import successful.")
    
    print("Testing execution (Forcing Fallback)...")
    if "TAVILY_API_KEY" in os.environ:
        del os.environ["TAVILY_API_KEY"]
        
    try:
        result = run_researcher("Test query")
        print("Execution successful:", result)
    except Exception as e:
        print(f"Execution failed: {e}")
        import traceback
        traceback.print_exc()

except Exception as e:
    print(f"Import failed: {e}")
    import traceback
    traceback.print_exc()
