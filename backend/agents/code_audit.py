import os
import concurrent.futures
import json
import time

# Configuration
MODEL = "llama3.1:70b-instruct-q8_0"
OUTPUT_FILE = "audit_report.md"
TARGET_DIRS = {
    "Security": ["backend/", "app/api/"],
    "Performance": ["app/", "components/"],
    "Architecture": ["app/", "lib/", "backend/"],
    "Testing": ["app/", "backend/"] # Focused scope for E2E suite generation
}

class CodeAuditOrchestrator:
    def __init__(self):
        print(f"🕵️  Audit Orchestrator: Initialized (Model: {MODEL})", flush=True)

    def run_agent(self, agent_name, dirs):
        import requests
        print(f"🚀 Launching Agent: {agent_name}...", flush=True)
        
        # Collect code snippets (simplified for logic demo, restricted to first few files)
        code_context = ""
        for d in dirs:
            if os.path.isfile(d):
                with open(d, 'r') as f:
                    code_context += f"\nFILE: {d}\n{f.read()[:4000]}\n"
            elif os.path.isdir(d):
                for root, _, files in os.walk(d):
                    for file in files[:10]: # Increased to 10 files per dir
                        if file.endswith(('.ts', '.tsx', '.py', '.js')):
                            path = os.path.join(root, file)
                            with open(path, 'r') as f:
                                code_context += f"\nFILE: {path}\n{f.read()[:4000]}\n"

        prompts = {
            "Security": "Analyze this code for security vulnerabilities, insecure API patterns, and secret leaks. Provide a detailed markdown report.",
            "Performance": "Identify React re-render bottlenecks, heavy memory usage, and performance anti-patterns. Provide a detailed markdown report.",
            "Architecture": "Propose a migration from Zustand (found in node_modules) to Next.js 'Server Actions' and React 19 features (useActionState, etc.). Provide a transformation roadmap.",
            "Testing": "Generate a comprehensive Playwright E2E test suite in TypeScript for these modules. Output code directly."
        }

        prompt = f"{prompts[agent_name]}\n\nCODE CONTEXT:\n{code_context}"
        
        try:
            response = requests.post("http://localhost:11434/api/generate", 
                                   json={"model": MODEL, "prompt": prompt, "stream": False},
                                   timeout=3600)
            res_json = response.json()
            print(f"✅ Agent {agent_name} Finished.", flush=True)
            return f"## Agent: {agent_name} Audit Result\n\n{res_json['response']}\n\n"
        except Exception as e:
            print(f"❌ Agent {agent_name} Failed: {e}", flush=True)
            return f"## Agent: {agent_name} Audit Result\n\nFAILED: {e}\n\n"

    def execute_audit(self):
        print(f"🔥 Starting SEQUENTIAL Audit Blast (Model: {MODEL})...", flush=True)
        
        header = "# Master Architect Report: Nexus-AI High-Precision Audit\n\n"
        header += f"Generated on: {time.strftime('%Y-%m-%d %H:%M:%S')}\n"
        header += f"Model: {MODEL}\n\n"
        
        if not os.path.exists(OUTPUT_FILE):
            with open(OUTPUT_FILE, "w") as f:
                f.write(header)
        
        start_time = time.time()
        
        for name, dirs in TARGET_DIRS.items():
            # Resumable check
            if os.path.exists(OUTPUT_FILE):
                with open(OUTPUT_FILE, "r") as f:
                    content = f.read()
                    if f"## Agent: {name} Audit Result" in content and "FAILED" not in content:
                        print(f"⏩ Skipping {name} (Already in report).", flush=True)
                        continue

            result = self.run_agent(name, dirs)
            with open(OUTPUT_FILE, "a") as f:
                f.write(result)
            print(f"💾 Persisted {name} results to {OUTPUT_FILE}", flush=True)

        end_time = time.time()
        print(f"✨ Audit Complete in {end_time - start_time:.1f}s. Report saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    orchestrator = CodeAuditOrchestrator()
    orchestrator.execute_audit()
