import os
import sys

# Add current directory to path
sys.path.append(os.getcwd())

from backend.hierarchical_rag import folder_summarizer, hierarchical_index
from backend.ingest import ingest_documents
from backend.rag import rag_service

def test_hierarchical_flow():
    print("--- 1. Testing Folder Summarization (16 cores) ---")
    base_paths = [os.path.abspath("./backend")]
    folder_data = folder_summarizer.scan_and_summarize(base_paths)
    print(f"Generated {len(folder_data)} folder summaries.")
    hierarchical_index.save_index(folder_data)
    
    print("\n--- 2. Testing RAM-Resident Index Search ---")
    query = "Find the code for managing memory in the backend."
    relevant_folders = hierarchical_index.search_folders(query)
    print(f"Query: {query}")
    print(f"Identified Folders: {relevant_folders}")
    
    # Check if memory_manager.py's folder is found
    # Expected folder: /Users/rohitchandra/Documents/AI/backend
    
    print("\n--- 3. Testing Two-Step RAG Query ---")
    query_gen = rag_service.query("What does the memory manager do?")
    for chunk in query_gen:
        print(chunk, end="", flush=True)
    print("\n")

if __name__ == "__main__":
    test_hierarchical_flow()
