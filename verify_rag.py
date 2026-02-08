import os
import sys

# Ensure backend can be imported
sys.path.append(os.getcwd())

try:
    print("Importing rag_service...")
    from backend.rag import rag_service
    
    print(f"RAG Service Initialized: {rag_service}")
    print(f"Embeddings: {rag_service.embeddings}")
    
    print("Attempting to initialize vector store explicitly...")
    try:
        rag_service.initialize_vector_store()
        print(f"Vector Store: {rag_service.vector_store}")
        if rag_service.vector_store:
            print(f"Client: {rag_service.vector_store._client}")
    except Exception as e:
        print(f"Error initializing vector store: {e}")
        import traceback
        traceback.print_exc()

except Exception as e:
    print(f"Import Failed: {e}")
