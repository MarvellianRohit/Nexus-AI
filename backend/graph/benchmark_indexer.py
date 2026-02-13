import time
from backend.graph.semantic_indexer import SemanticIndexer

def benchmark():
    print("🏎️ Starting Semantic Indexer Benchmark...")
    start_time = time.time()
    
    indexer = SemanticIndexer()
    try:
        indexer.run()
    finally:
        indexer.close()
    
    end_time = time.time()
    duration = end_time - start_time
    print(f"🏁 Benchmark Complete in {duration:.2f} seconds.")

if __name__ == "__main__":
    benchmark()
