import os
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader, TextLoader
from langchain_community.embeddings.huggingface import HuggingFaceEmbeddings
from langchain_community.chat_models import ChatOllama
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_core.prompts import ChatPromptTemplate
from typing import List

# Configuration
MODEL_NAME = "llama3" 
CHROMA_PATH = "chroma_db"
# High performance local embeddings
EMBEDDING_MODEL_NAME = "sentence-transformers/all-mpnet-base-v2"

class RAGService:
    def __init__(self):
        self.vector_store = None
        self.retriever = None
        self.model = ChatOllama(model=MODEL_NAME, timeout=300)
        print("Loading Embeddings Model (may take a moment)...")
        self.embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)

    def initialize_vector_store(self):
        """Initializes the vector store from existing persistence."""
        chroma_host = os.getenv("CHROMA_SERVER_HOST")
        chroma_port = os.getenv("CHROMA_SERVER_PORT", "8000")

        if chroma_host:
            print(f"Connecting to ChromaDB Server at {chroma_host}:{chroma_port}...")
            import chromadb
            from chromadb.config import Settings
            
            client = chromadb.HttpClient(host=chroma_host, port=int(chroma_port))
            self.vector_store = Chroma(
                client=client,
                embedding_function=self.embeddings,
                collection_name="nexus_ai"
            )
        elif os.path.exists(CHROMA_PATH):
             self.vector_store = Chroma(
                persist_directory=CHROMA_PATH, 
                embedding_function=self.embeddings
            )
        else:
            print("No local vector store found and no server configured.")
            return

        # Memory optimization: fetch k=5
        self.retriever = self.vector_store.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 5}
        )
        print("Vector store initialized.")

    def generate_sub_questions(self, question: str) -> List[str]:
        """Reflective Search: Generate 3 sub-questions."""
        prompt = f"""You are an AI research assistant. Break down the following user question into 3 distinct, searchable sub-questions that will help answer the main question comprehensively. 
        Output ONLY the 3 questions, separated by newlines.
        
        User Question: {question}
        """
        response = self.model.invoke(prompt)
        questions = [q.strip() for q in response.content.split('\n') if q.strip()]
        return questions[:3]

    def query(self, question: str):
        if not self.vector_store:
            yield "System Initializing..."
            self.initialize_vector_store()
            if not self.vector_store:
                yield "RAG system not initialized. Please ingest documents first."
                return

        # 1. Reflective Step
        yield "🤔 Analyzing query complexity...\n"
        sub_questions = self.generate_sub_questions(question)
        if not sub_questions:
            sub_questions = [question] # Fallback
        
        context_docs = []
        for q in sub_questions:
            yield f"🔍 Searching: {q}...\n"
            docs = self.retriever.get_relevant_documents(q)
            context_docs.extend(docs)
        
        # Deduplicate
        unique_docs = {doc.page_content: doc for doc in context_docs}.values()
        context_text = "\n\n".join([d.page_content for d in unique_docs])
        
        yield "💡 Synthesizing final answer...\n\n"
        
        # 2. Synthesis Step
        template = """Answer the question based only on the following context:
{context}

Question: {question}
"""
        prompt = ChatPromptTemplate.from_template(template)
        
        chain = (
            {"context": lambda x: context_text, "question": RunnablePassthrough()}
            | prompt
            | self.model
            | StrOutputParser()
        )
        
        for chunk in chain.stream(question):
            yield chunk

rag_service = RAGService()
# Auto-init on load if possible
try:
    rag_service.initialize_vector_store()
except:
    pass
