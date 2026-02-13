import json
import threading
import concurrent.futures
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from backend.mlx_engine import mlx_engine

class MissionPlan(BaseModel):
    task_name: str
    steps: List[str]
    coder_instructions: str
    tester_instructions: str
    linter_rules: List[str]

class WorkerResult(BaseModel):
    worker_type: str
    success: bool
    output: str
    error: Optional[str] = None

class PlanningAgent:
    def generate_plan(self, task: str) -> MissionPlan:
        print("🧠 [Mission Control] Consulting Llama-3.3-70B Planner...")
        prompt = f"""You are the Nexus-AI Mission Planner. Deconstruct the following task into a structured JSON mission plan.
Task: {task}

Output ONLY valid JSON in this format:
{{
  "task_name": "string",
  "steps": ["step1", "step2"],
  "coder_instructions": "detailed coding guide",
  "tester_instructions": "testing requirements",
  "linter_rules": ["rule1", "rule2"]
}}
"""
        response = mlx_engine.generate_response(prompt, model_key="planner")
        try:
            # Simple JSON extraction in case model adds prose
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            data = json.loads(response[json_start:json_end])
            return MissionPlan(**data)
        except Exception as e:
            print(f"❌ Planning Error: {e}\nRaw Response: {response}")
            # Fallback plan
            return MissionPlan(
                task_name="Fallback Mission",
                steps=["Execute task directly"],
                coder_instructions=task,
                tester_instructions="Verify manually",
                linter_rules=["Standard PEP8"]
            )

class WorkerAgent:
    def __init__(self, worker_type: str, model_key: str):
        self.worker_type = worker_type
        self.model_key = model_key

    def execute(self, instructions: str, shared_context: str = "") -> WorkerResult:
        print(f"👷 [Worker-{self.worker_type}] Starting work...")
        prompt = f"Role: {self.worker_type}\nInstructions: {instructions}\nContext: {shared_context}\nProvide your technical output."
        output = mlx_engine.generate_response(prompt, model_key=self.model_key)
        
        # Simulate local verification check
        success = "error" not in output.lower()
        return WorkerResult(worker_type=self.worker_type, success=success, output=output)

class Orchestrator:
    def __init__(self):
        self.planner = PlanningAgent()
        self.coder = WorkerAgent("Coder", "logic")
        self.tester = WorkerAgent("Tester", "logic")
        self.linter = WorkerAgent("Linter", "turbo")

    def run_mission(self, task: str):
        # 1. Plan
        plan = self.planner.generate_plan(task)
        print(f"📝 Mission Plan Confirmed: {plan.task_name}")

        # 2. Parallel Execution
        results = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            future_to_worker = {
                executor.submit(self.coder.execute, plan.coder_instructions): "Coder",
                executor.submit(self.tester.execute, plan.tester_instructions): "Tester",
                executor.submit(self.linter.execute, ". ".join(plan.linter_rules)): "Linter"
            }
            
            for future in concurrent.futures.as_completed(future_to_worker):
                worker_name = future_to_worker[future]
                try:
                    res = future.result()
                    results.append(res)
                    print(f"✅ {worker_name} returned success: {res.success}")
                except Exception as exc:
                    print(f"❌ {worker_name} generated an exception: {exc}")
                    results.append(WorkerResult(worker_type=worker_name, success=False, output="", error=str(exc)))

        # 3. Decision Logic
        all_success = all(r.success for r in results)
        
        # Aggregate Report
        report = f"# MISSION REPORT: {plan.task_name}\n\n"
        report += f"**Status**: {'✅ COMPLETE' if all_success else '❌ PARTIAL FAILURE'}\n\n"
        for r in results:
            report += f"## {r.worker_type} Result\n{r.output[:500]}...\n\n"

        return report

mission_control = Orchestrator()
