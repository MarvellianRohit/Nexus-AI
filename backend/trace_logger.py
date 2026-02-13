import json
import os
import uuid
import datetime
from typing import List, Dict, Any, Optional

TRACE_FILE = "traces.jsonl"

class TraceLogger:
    def __init__(self, trace_file=TRACE_FILE):
        self.trace_file = trace_file

    def create_trace(self, prompt: str, system_prompt: str = "") -> str:
        """Initializes a new trace and returns a unique trace_id."""
        trace_id = str(uuid.uuid4())
        entry = {
            "trace_id": trace_id,
            "timestamp": datetime.datetime.now().isoformat(),
            "prompt": prompt,
            "system_prompt": system_prompt,
            "thoughts": [],
            "tool_calls": [],
            "final_answer": "",
            "feedback": None # 1 for up, 0 for down
        }
        self._write_entry(entry)
        return trace_id

    def log_thought(self, trace_id: str, thought: str):
        """Appends a thought step to the trace."""
        self._update_entry(trace_id, "thoughts", thought, append=True)

    def log_tool_call(self, trace_id: str, tool_name: str, arguments: Dict[str, Any], result: Any):
        """Logs a tool call and its result."""
        tool_entry = {
            "tool": tool_name,
            "args": arguments,
            "result": str(result),
            "timestamp": datetime.datetime.now().isoformat()
        }
        self._update_entry(trace_id, "tool_calls", tool_entry, append=True)

    def log_final_answer(self, trace_id: str, answer: str):
        """Logs the final response sent to the user."""
        self._update_entry(trace_id, "final_answer", answer)

    def log_feedback(self, trace_id: str, score: int):
        """Logs user feedback (1 or 0)."""
        self._update_entry(trace_id, "feedback", score)

    def _write_entry(self, entry: Dict):
        with open(self.trace_file, "a") as f:
            f.write(json.dumps(entry) + "\n")

    def _update_entry(self, trace_id: str, key: str, value: Any, append: bool = False):
        """
        Updates an existing entry in the JSONL file. 
        Note: For performance in a real system, we'd use a database. 
        In this local setup, we rewrite the line if it's small or handle it in memory.
        For simplicity, we'll read all, update, and rewrite.
        """
        lines = []
        if os.path.exists(self.trace_file):
            with open(self.trace_file, "r") as f:
                lines = f.readlines()
        
        with open(self.trace_file, "w") as f:
            for line in lines:
                try:
                    entry = json.loads(line)
                    if entry.get("trace_id") == trace_id:
                        if append:
                            if isinstance(entry.get(key), list):
                                entry[key].append(value)
                            else:
                                entry[key] = [value]
                        else:
                            entry[key] = value
                    f.write(json.dumps(entry) + "\n")
                except:
                    f.write(line)

trace_logger = TraceLogger()
