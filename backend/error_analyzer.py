import json
import os
from backend.mlx_engine import mlx_engine

TRACE_FILE = "traces.jsonl"
UPDATES_FILE = "backend/system_prompt_updates.md"

class ErrorAnalyzer:
    def __init__(self, trace_file=TRACE_FILE, updates_file=UPDATES_FILE):
        self.trace_file = trace_file
        self.updates_file = updates_file

    def analyze_errors(self):
        """Analyzes downvoted responses and updates the system prompt."""
        if not os.path.exists(self.trace_file):
            print("No traces found.")
            return

        downvoted_traces = []
        with open(self.trace_file, "r") as f:
            for line in f:
                try:
                    entry = json.loads(line)
                    if entry.get("feedback") == 0:
                        downvoted_traces.append(entry)
                except:
                    continue

        if not downvoted_traces:
            print("No downvoted responses to analyze.")
            return

        print(f"Analyzing {len(downvoted_traces)} failed responses with Llama-3-70B...")

        # Format traces for analysis
        analysis_context = ""
        for i, trace in enumerate(downvoted_traces):
            analysis_context += f"--- FAILED INTERACTION {i+1} ---\n"
            analysis_context += f"User Prompt: {trace['prompt']}\n"
            analysis_context += f"AI Thought Chain: {'. '.join(trace['thoughts'])}\n"
            analysis_context += f"AI Final Answer: {trace['final_answer']}\n\n"

        prompt = f"""You are a Meta-Cognitive Error Analyzer. Your task is to analyze the following failed AI interactions and identify recurring patterns of errors, hallucinations, or poor formatting.

FAILED INTERACTIONS:
{analysis_context}

Based on these failures, generate a set of 'Continuous Improvement Rules' for the system prompt.
These rules should be highly specific and actionable (e.g., 'Never assume X when the user asks Y', 'Always format Z using tags').

Output ONLY the rules in a clear markdown bulleted list.
"""
        # Use the "reasoning" model (Llama-3-70B)
        improvements = mlx_engine.generate_response(prompt, model_key="reasoning")
        
        # Save updates
        with open(self.updates_file, "w") as f:
            f.write("# Automated System Prompt Improvements\n\n")
            f.write("> [!NOTE]\n")
            f.write("> These rules were automatically generated from user feedback analysis.\n\n")
            f.write(improvements)
        
        print(f"System prompt updates saved to {self.updates_file}")

if __name__ == "__main__":
    analyzer = ErrorAnalyzer()
    analyzer.analyze_errors()
