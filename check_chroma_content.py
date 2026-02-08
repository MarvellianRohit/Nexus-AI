import chromadb
import os
import sys

# Add path to find backend
sys.path.append(os.getcwd())
from backend.rag import CHROMA_PATH

print(f"Checking ChromaDB at: {CHROMA_PATH}")

if not os.path.exists(CHROMA_PATH):
    print("❌ Path does not exist!")
    sys.exit(1)

try:
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    collections = client.list_collections()
    print(f"Found {len(collections)} collections:")
    for col in collections:
        print(f" - {col.name} (Count: {col.count()})")
        
    # Check specifically nexus_architect
    try:
        col = client.get_collection("nexus_architect")
        print(f"✅ 'nexus_architect' exists with {col.count()} docs.")
        if col.count() == 0:
             print("⚠️ Collection is empty!")
    except Exception as e:
        print(f"❌ 'nexus_architect' not found: {e}")

except Exception as e:
    print(f"Error accessing DB: {e}")
