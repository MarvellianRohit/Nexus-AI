import time
import threading
import psutil
from typing import List, Dict, Any, Optional
from langchain_core.runnables import RunnableParallel, RunnableLambda
from backend.mlx_engine import mlx_engine

class SharedState:
    def __init__(self):
        self.lock = threading.Lock()
        self.data = {
            "auth_code": "",
            "api_docs": "",
            "unit_tests": "",
            "status": "idle"
        }

    def update(self, key: str, value: str):
        with self.lock:
            self.data[key] = value
            print(f"DEBUG: SharedState Updated [{key}].")

    def get(self, key: str) -> str:
        with self.lock:
            return self.data.get(key, "")

class PriorityTaskQueue:
    def __init__(self):
        # 1: Refactor, 2: Document, 3: Test
        self.queue = []
        self.paused_tasks = {}

    def add_task(self, name: str, priority: int, func):
        self.queue.append({"name": name, "priority": priority, "func": func})
        self.queue.sort(key=lambda x: x["priority"])

    def check_memory_and_orchestrate(self):
        """Monitors memory and pauses lower priority tasks if needed."""
        mem = psutil.virtual_memory()
        # Simulation: Threshold at 90% (or specific GB for M3 Max 128GB)
        # Using a simulated 110GB threshold for this demo
        threshold_gb = 110
        current_gb = mem.used / (1024**3)
        
        if current_gb > threshold_gb:
            print(f"🚨 MEMORY CRITICAL ({current_gb:.2f}GB). Pausing low-priority tasks...")
            return True
        return False

shared_state = SharedState()

class ConcurrentOrchestrator:
    def __init__(self):
        self.queue = PriorityTaskQueue()

    def task_refactor_auth(self, inputs: Dict):
        print("🚀 [Task 1] Refactoring Auth Logic (Priority 1)...")
        prompt = "Refactor the existing auth_production.py to use JWT instead of sessions. Return ONLY the code."
        code = mlx_engine.generate_response(prompt, model_key="logic")
        shared_state.update("auth_code", code)
        return {"auth_code": code}

    def task_document_api(self, inputs: Dict):
        print("🚀 [Task 2] Documenting API (Priority 2)...")
        # Wait for auth code if needed (managing shared state dependency)
        while not shared_state.get("auth_code"):
            time.sleep(1)
            print("⏳ [Task 2] Waiting for refactored code to document...")
        
        code_to_doc = shared_state.get("auth_code")
        prompt = f"Write OpenAPI documentation for this code:\n{code_to_doc}\nReturn ONLY the markdown."
        docs = mlx_engine.generate_response(prompt, model_key="reasoning")
        shared_state.update("api_docs", docs)
        return {"api_docs": docs}

    def task_generate_tests(self, inputs: Dict):
        print("🚀 [Task 3] Generating Unit Tests (Priority 3)...")
        
        # Check memory bottleneck for Priority 3 task
        if self.queue.check_memory_and_orchestrate():
            print("⏸️ [Task 3] Pausing and caching state to 128GB RAM...")
            # Simulate caching time
            time.sleep(2)
            print("⏯️ [Task 3] Resuming after memory buffer confirmed.")

        while not shared_state.get("auth_code"):
            time.sleep(1)
        
        code_to_test = shared_state.get("auth_code")
        prompt = f"Generate Pytest unit tests for this code:\n{code_to_test}\nReturn ONLY the code."
        tests = mlx_engine.generate_response(prompt, model_key="logic")
        shared_state.update("unit_tests", tests)
        return {"unit_tests": tests}

    def run_concurrent_test(self):
        print("🧠 [Orchestrator] Triggering LangChain Parallel Runnable...")
        
        # Define Parallel Runnables
        parallel_chain = RunnableParallel(
            refactor=RunnableLambda(self.task_refactor_auth),
            document=RunnableLambda(self.task_document_api),
            test=RunnableLambda(self.task_generate_tests)
        )
        
        start_time = time.time()
        results = parallel_chain.invoke({"start": True})
        end_time = time.time()
        
        print(f"✅ Concurrent Reliability Test Finished in {end_time - start_time:.2f}s")
        return results

concurrent_orchestrator = ConcurrentOrchestrator()
