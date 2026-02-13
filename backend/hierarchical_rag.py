import os
import json
import concurrent.futures
from typing import List, Dict
import numpy as np
from backend.mlx_engine import mlx_engine

class FolderSummarizer:
    def __init__(self, max_workers=16):
        self.max_workers = max_workers

    def summarize_folder(self, folder_path: str, files: List[str]) -> Dict:
        """Generates a 1-paragraph summary of a folder based on its files."""
        file_list_str = "\n".join(files[:20]) # Limit to 20 files for context
        if len(files) > 20:
            file_list_str += f"\n... and {len(files) - 20} more files."

        prompt = f"""You are an expert software architect. Analyze the following folder content and its file list.
Folder Path: {folder_path}
Files:
{file_list_str}

Provide a concise 1-paragraph summary (max 100 words) describing the primary purpose and responsibility of this folder in the codebase.
Return ONLY the summary paragraph.
"""
        summary = mlx_engine.generate_response(prompt, model_key="turbo")
        return {"folder": folder_path, "summary": summary.strip()}

    def scan_and_summarize(self, base_paths: List[str]) -> List[Dict]:
        """Scans directories and summarizes each folder in parallel."""
        folder_data = []
        
        folders_to_process = []
        for base_path in base_paths:
            for root, dirs, files in os.walk(base_path):
                # Filter out hidden/ignored dirs
                dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ('node_modules', 'dist', 'build', '__pycache__')]
                
                if files:
                    # Filter for relevant code files
                    code_files = [f for f in files if f.endswith(('.py', '.ts', '.tsx', '.js', '.md', '.pdf', '.c', '.cpp', '.h'))]
                    if code_files:
                        folders_to_process.append((root, code_files))

        print(f"Summarizing {len(folders_to_process)} folders using {self.max_workers} workers...")
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_folder = {executor.submit(self.summarize_folder, f[0], f[1]): f[0] for f in folders_to_process}
            for future in concurrent.futures.as_completed(future_to_folder):
                try:
                    data = future.result()
                    folder_data.append(data)
                except Exception as exc:
                    print(f"Folder summarization generated an exception: {exc}")
        
        return folder_data

class TopLevelIndex:
    def __init__(self, summary_file="folder_summaries.json"):
        self.summary_file = summary_file
        self.summaries: List[Dict] = []
        self.embeddings: np.ndarray = None
        self.load_index()

    def load_index(self):
        """Loads summaries from disk into RAM."""
        if os.path.exists(self.summary_file):
            with open(self.summary_file, 'r') as f:
                self.summaries = json.load(f)
            print(f"Loaded {len(self.summaries)} folder summaries into RAM.")
            # In a real implementation with vector search, we would pre-compute 
            # embeddings here and store them in a numpy array for 400GB/s M3 Max speed.
            # For this demo, we'll use MLX or a lightweight embedding model.
        else:
            print("No top-level index found. Need to run ingestion.")

    def save_index(self, folder_data: List[Dict]):
        self.summaries = folder_data
        with open(self.summary_file, 'w') as f:
            json.dump(folder_data, f, indent=2)
        print(f"Saved {len(folder_data)} summaries to {self.summary_file}.")

    def search_folders(self, query: str, top_k=3) -> List[str]:
        """Search the summaries to find the most relevant folders."""
        if not self.summaries:
            return []

        # Simple semantic search using MLX for ranking
        # Ideally, we'd use a local embedding model for sub-millisecond search.
        # But for this task, we'll simulate the "High-speed" search by comparing
        # the query against the summaries. 
        
        # Optimization: Use MLX to pick the best folders from the summaries.
        summaries_blob = ""
        for i, item in enumerate(self.summaries):
            summaries_blob += f"ID: {i} | Path: {item['folder']}\nSummary: {item['summary']}\n\n"

        prompt = f"""Given the following folder summaries and the user query, identify the {top_k} most relevant folder paths that likely contain the answer.
Query: {query}

Summaries:
{summaries_blob}

Return ONLY a comma-separated list of the Folder Paths.
"""
        response = mlx_engine.generate_response(prompt, model_key="turbo")
        relevant_paths = [p.strip() for p in response.split(',') if p.strip()]
        return relevant_paths[:top_k]

hierarchical_index = TopLevelIndex()
folder_summarizer = FolderSummarizer(max_workers=16)
