import os
import shutil
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter, Language
from langchain_community.vectorstores import Chroma
from backend.rag import rag_service, CHROMA_PATH

# Exclusions
EXCLUDE_DIRS = {
    "node_modules", ".git", ".next", "venv", "__pycache__", 
    ".gemini", "dist", "build", "coverage", ".vscode", ".idea"
}

# Supported Extensions
EXTENSIONS = {".tsx", ".ts", ".py", ".js", ".json", ".css", ".md"}

def crawl_codebase(root_dir):
    documents = []
    print(f"🔍 Scanning codebase at {root_dir}...")
    
    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Filter directories in-place
        dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS]
        
        for file in filenames:
            ext = os.path.splitext(file)[1]
            if ext in EXTENSIONS:
                file_path = os.path.join(dirpath, file)
                try:
                    loader = TextLoader(file_path, encoding='utf-8')
                    documents.extend(loader.load())
                except Exception as e:
                    # Skip files that fail to load (binary, huge, etc)
                    pass
                    
    return documents

def ingest_codebase():
    root_path = os.path.abspath(".")
    
    # 1. Load Code
    docs = crawl_codebase(root_path)
    if not docs:
        return {"status": "error", "message": "No code files found."}
    
    print(f"✅ Loaded {len(docs)} code files.")

    # 2. Split Code
    # We use a generic splitter, but for optimal results we could use from_language
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=2000, # Larger chunks for context
        chunk_overlap=200,
        add_start_index=True,
    )
    chunks = text_splitter.split_documents(docs)
    print(f"✂️ Split into {len(chunks)} code chunks.")

    # 3. Add to ChromaDB (Reuse Client from RAG Service if available to avoid locks/errors)
    COLLECTION_NAME = "nexus_architect"
    
    # Try to get client from initialized RAG service
    client = None
    if rag_service.vector_store:
        try:
            client = rag_service.vector_store._client
            print("🔗 Reusing existing Chroma Client from RAG Service.")
        except:
            pass
            
    if client:
        # Use shared client
        try:
            # We can't easily delete collection via client if it's generic, 
            # but we can try client.delete_collection(COLLECTION_NAME)
            try:
                client.delete_collection(COLLECTION_NAME)
            except:
                pass
                
            vector_store = Chroma.from_documents(
                documents=chunks, 
                embedding=rag_service.embeddings,
                client=client,
                collection_name=COLLECTION_NAME
            )
            return {"status": "success", "chunks": len(chunks), "collection": COLLECTION_NAME, "method": "shared_client"}
        except Exception as e:
            return {"status": "error", "message": f"Shared Client Ingest Failed: {str(e)}"}

    # Fallback to independent init (Only if RAG service is dead)
    chroma_host = os.getenv("CHROMA_SERVER_HOST")
    chroma_port = os.getenv("CHROMA_SERVER_PORT", "8000")
    
    if chroma_host:
        import chromadb
        print(f"💾 Ingesting into ChromaDB Server ({COLLECTION_NAME})...")
        try:
            client = chromadb.HttpClient(host=chroma_host, port=int(chroma_port))
            try:
                client.delete_collection(COLLECTION_NAME)
            except:
                pass
                
            vector_store = Chroma.from_documents(
                documents=chunks, 
                embedding=rag_service.embeddings,
                client=client,
                collection_name=COLLECTION_NAME
            )
        except Exception as e:
            return {"status": "error", "message": str(e)}
            
    else:
        # Local Mode
        print(f"💾 Ingesting into Local Storage ({COLLECTION_NAME})...")
        try:
            import chromadb
            client = chromadb.PersistentClient(path=CHROMA_PATH)
            vector_store = Chroma(
                client=client,
                collection_name=COLLECTION_NAME,
                embedding_function=rag_service.embeddings
            )
            vector_store.add_documents(documents=chunks)
            print(f"✅ Added {len(chunks)} chunks to {COLLECTION_NAME}")
        except Exception as e:
             return {"status": "error", "message": f"Local Ingest Failed: {str(e)}"}

    return {"status": "success", "chunks": len(chunks), "collection": COLLECTION_NAME}

if __name__ == "__main__":
    ingest_codebase()
