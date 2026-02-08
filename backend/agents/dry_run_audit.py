import os
import concurrent.futures
import json
import requests
import time

# Configuration for DRY RUN
MODEL = "phi3:mini"
OUTPUT_FILE = "dry_run_audit_report.md"
TARGET_DIRS = {
    "Security": ["backend/server.py", "app/api/"],
    "Performance": ["app/", "components/"],
    "Architecture": ["app/", "lib/", "backend/server.py"],
    "Testing": ["."]
}

class CodeAuditOrchestrator:
    def __init__(self):
        print(f"🕵️  Dry Run Orchestrator: Initialized (Model: {MODEL})")

    def run_agent(self, agent_name, dirs):
        print(f"🚀 Launching Agent: {agent_name}...")
        
        code_context = ""
        for d in dirs:
            if os.path.isfile(d):
                with open(d, 'r') as f:
                    code_context += f"\nFILE: {d}\n{f.read()[:500]}\n"
            elif os.path.isdir(d):
                for root, _, files in os.walk(d):
                    for file in files[:2]: 
                        if file.endswith(('.ts', '.tsx', '.py', '.js')):
                            path = os.path.join(root, file)
                            with open(path, 'r') as f:
                                code_context += f"\nFILE: {path}\n{f.read()[:500]}\n"

        prompts = {
            "Security": "Check for obvious security issues.",
            "Performance": "Check for obvious performance issues.",
            "Architecture": "Suggest server actions migration.",
            "Testing": "Generate a simple playwright test."
        }

        prompt = f"{prompts[agent_name]}\n\nCODE CONTEXT:\n{code_context}"
        
        try:
            response = requests.post("http://localhost:11434/api/generate", 
                                   json={"model": MODEL, "prompt": prompt, "stream": False},
                                   timeout=30)
            res_json = response.json()
            return f"## Agent: {agent_name} Result\n\n{res_json['response']}\n\n"
        except Exception as e:
            return f"## Agent: {agent_name} Result\n\nFAILED: {e}\n\n"

    def execute_audit(self):
        print(f"🔥 Starting DRY RUN...")
        results = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            futures = {executor.submit(self.run_agent, name, dirs): name for name, dirs in TARGET_DIRS.items()}
            for future in concurrent.futures.as_completed(futures):
                results.append(future.result())

        with open(OUTPUT_FILE, "w") as f:
            f.write("# Dry Run Audit Report\n\n" + "".join(results))
        print(f"✨ Dry Run Complete. Report: {OUTPUT_FILE}")

if __name__ == "__main__":
    orchestrator = CodeAuditOrchestrator()
    orchestrator.execute_audit()
