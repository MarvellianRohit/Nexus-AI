import os
import shutil
from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from backend.rag import rag_service, CHROMA_PATH

# User's Research folder + Current Repo
DATA_PATHS = [
    os.path.expanduser("~/Documents/Research"), # Hypothetical path from prompt
    os.path.abspath(".") # Current Repo
]

def ingest_documents():
    """Scans Research folder and Repo."""
    
    docs = []
    
    for path in DATA_PATHS:
        if not os.path.exists(path):
            print(f"Path not found: {path}, skipping.")
            continue
            
        print(f"Scanning {path}...")
        
        # Loaders
        # Exclude node_modules, .git, etc via glob if using DirectoryLoader is tricky, 
        # but RecursiveCharacterTextSplitter handles content. 
        # For simplicity, we'll try to load specific extensions.
        
        loaders = [
            DirectoryLoader(path, glob="**/*.pdf", loader_cls=PyPDFLoader, show_progress=True),
            DirectoryLoader(path, glob="**/*.txt", loader_cls=TextLoader, show_progress=True),
            DirectoryLoader(path, glob="**/*.md", loader_cls=TextLoader, show_progress=True),
            DirectoryLoader(path, glob="**/*.tsx", loader_cls=TextLoader, show_progress=True),
            DirectoryLoader(path, glob="**/*.ts", loader_cls=TextLoader, show_progress=True),
            DirectoryLoader(path, glob="**/*.py", loader_cls=TextLoader, show_progress=True)
        ]
        
        for loader in loaders:
            try:
                loaded = loader.load()
                docs.extend(loaded)
                print(f"Loaded {len(loaded)} docs from {loader.glob}")
            except Exception as e:
                # directory loader sometimes fails on single files, ignore
                continue

    if not docs:
        return {"status": "error", "message": "No documents found."}

    # 2. Split Text
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        add_start_index=True,
    )
    chunks = text_splitter.split_documents(docs)
    print(f"Split into {len(chunks)} chunks.")

    # 3. Add to ChromaDB
    # 3. Add to ChromaDB
    chroma_host = os.getenv("CHROMA_SERVER_HOST")
    chroma_port = os.getenv("CHROMA_SERVER_PORT", "8000")

    if chroma_host:
        import chromadb
        print(f"Ingesting into ChromaDB Server at {chroma_host}:{chroma_port}...")
        try:
            # Use HttpClient for remote server
            client = chromadb.HttpClient(host=chroma_host, port=int(chroma_port))
            try:
                client.delete_collection("nexus_ai")
            except:
                pass
            
            vector_store = Chroma.from_documents(
                documents=chunks, 
                embedding=rag_service.embeddings,
                client=client,
                collection_name="nexus_ai"
            )
        except Exception as e:
            return {"status": "error", "message": f"Server Connection Failed: {str(e)}"}
    
    else:
        # Local Mode using PersistentClient directly (Fixing 'http-only' error)
        print(f"Using Local Storage at {CHROMA_PATH}...")
        if os.path.exists(CHROMA_PATH):
            shutil.rmtree(CHROMA_PATH)
            
        vector_store = Chroma.from_documents(
            documents=chunks, 
            embedding=rag_service.embeddings,
            persist_directory=CHROMA_PATH
        )
    
    # Reload service
    rag_service.initialize_vector_store()
    
    return {"status": "success", "chunks": len(chunks)}

if __name__ == "__main__":
    ingest_documents()
