import json
import re
from backend.mlx_engine import mlx_engine

class DualAgentLoop:
    def __init__(self, max_turns=3):
        self.max_turns = max_turns
        self.architect_prompt = """You are the **Nexus Architect** (Llama-3-70B).
Your goal is to write high-performance, expert-level code based on user requests.
If you receive an error log from the Auditor, you MUST fix the issues and return the full corrected code.

User Request: {task}
{previous_feedback}

Return the code in a single code block. Include concise architectural explanations."""

        self.auditor_prompt = """You are the **Nexus Auditor** (Llama-3-70B).
Analyze the following code for:
1. Bugs or logic errors.
2. Security vulnerabilities.
3. Performance bottlenecks.

Code to analyze:
{code}

If you find issues, output:
FAIL: [Detailed list of bugs/issues]

If the code is professional and correct, output:
PASS: [Brief verification summary]

Be strict. Do not be overly polite."""

    def run(self, task: str):
        current_code = ""
        previous_feedback = ""
        
        for turn in range(self.max_turns):
            yield f"--- Turn {turn + 1}: Architect Drafting... ---\n\n"
            
            # 1. Architect Generates/Fixes
            arch_input = self.architect_prompt.format(
                task=task,
                previous_feedback=f"\nAuditor Feedback (Turn {turn}):\n{previous_feedback}" if previous_feedback else ""
            )
            
            current_code = mlx_engine.generate_response(arch_input, model_key="reasoning")
            
            yield f"--- Turn {turn + 1}: Auditor Verifying... ---\n\n"
            
            # 2. Auditor Verifies
            audit_input = self.auditor_prompt.format(code=current_code)
            audit_result = mlx_engine.generate_response(audit_input, model_key="reasoning").strip()
            
            print(f"Auditor Result: {audit_result[:100]}...")
            
            if audit_result.startswith("PASS"):
                yield f"✅ **Auditor Pass**: {audit_result[5:]}\n\n"
                yield current_code
                return
            else:
                previous_feedback = audit_result
                yield f"⚠️ **Auditor Review (Turn {turn + 1})**: {audit_result[5:]}\n\n"
                # If we're on the last turn, return the code anyway with warnings
                if turn == self.max_turns - 1:
                    yield "⚠️ **Dual Loop Exited**: Max trials reached. Use with caution.\n\n"
                    yield current_code
                    return

    def stream_loop(self, task: str):
        """Generator for FastAPI StreamingResponse."""
        # Force flush preamble
        yield " " * 1024 + "\n"
        yield "🚀 **Initializing Nexus-AI Dual-Agent Loop...**\n\n"
        
        for part in self.run(task):
            yield part

dual_agent_manager = DualAgentLoop()
