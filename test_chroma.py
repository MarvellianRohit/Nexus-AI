import chromadb
import os

try:
    print("Testing PersistentClient...")
    path = "test_chroma_db"
    if not os.path.exists(path):
        os.makedirs(path)
        
    client = chromadb.PersistentClient(path=path)
    print("Success!")
    # cleanup
    # import shutil
    # shutil.rmtree(path)
except Exception as e:
    print(f"FAILED: {e}")
    import traceback
    traceback.print_exc()
