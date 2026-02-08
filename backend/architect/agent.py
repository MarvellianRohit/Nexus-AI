from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_community.vectorstores import Chroma
from backend.rag import rag_service, CHROMA_PATH
import os

# Configuration
GOOGLE_API_KEY = "AIzaSyB0XcmiVCVDen-Qk0pwgadEiN2aAUGLkKU"
COLLECTION_NAME = "nexus_architect"

class ArchitectAgent:
    # ... (init methods)
    def __init__(self):
        # Independent Instance (Gemini 2.5 Pro) - Primary
        self.llm_pro = ChatGoogleGenerativeAI(
            model="gemini-2.5-pro",
            google_api_key=GOOGLE_API_KEY,
            convert_system_message_to_human=True,
            max_retries=0
        )
        # Fallback Instance (Gemini 2.5 Flash)
        self.llm_flash = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=GOOGLE_API_KEY,
            convert_system_message_to_human=True
        )
        
        # Connect to Architect Collection (Shared or Independent)
        # ... (Chroma init logic remains same) ...
        try:
            # Reuse Client from RAG Service (Primary Strategy)
            if rag_service.vector_store:
                print("🔗 Architect: Reusing Chroma Client from RAG Service.")
                self.vector_store = Chroma(
                    client=rag_service.vector_store._client,
                    collection_name=COLLECTION_NAME,
                    embedding_function=rag_service.embeddings
                )
            else:
                # Fallback (Likely to fail if server is running but RAG didn't init)
                print(f"📂 Architect: Trying independent init at {CHROMA_PATH}")
                import chromadb
                client = chromadb.PersistentClient(path=CHROMA_PATH)
                self.vector_store = Chroma(
                    client=client,
                    collection_name=COLLECTION_NAME,
                    embedding_function=rag_service.embeddings
                )
                
            self.retriever = self.vector_store.as_retriever(search_kwargs={"k": 20}) 
        except Exception as e:
            print(f"⚠️ Architect Chroma Init Failed: {e}")
            self.vector_store = None
            self.retriever = None

        # AUDIT PROMPT
        self.audit_prompt = ChatPromptTemplate.from_template("""You are the **Nexus Architect**, a senior software engineer and system architect.
Your goal is to perform a **Global Code Audit** of the provided codebase context.

Current Context (Code Snippets):
{context}

User Instruction: 
Perform a Global Code Audit looking for:
1. Redundant React components.
2. Type safety issues in TypeScript (any 'any' types, missing interfaces).
3. Potential performance bottlenecks in Next.js API routes or logic.

Output Requirement:
- Output a **Detailed Markdown Report**.
- Group findings by category (Redundancy, Types, Performance).
- **CRITICAL**: Provide specific **Code Snippets** for the fixes. Show 'Before' and 'After'.
- Be strict and professional.

Report:""")
        
        # Chains
        self.chain_pro = self.audit_prompt | self.llm_pro | StrOutputParser()
        self.chain_flash = self.audit_prompt | self.llm_flash | StrOutputParser()

    def run_audit(self):
        """
        Retrieves context and runs the global audit with fallback.
        """
        if not self.retriever:
            yield "⚠️ Architect Service Unavailable (Chroma Init Failed)."
            return

        try:
            # 1. Retrieve Context
            docs = self.retriever.get_relevant_documents("React Components Next.js API Routes TypeScript Interfaces Redundant Code")
            context_text = "\n\n".join([d.page_content for d in docs])
            
            if not context_text:
                yield "⚠️ No codebase index found. Please run the 'Ingest Codebase' action first."
                return

            yield "🔍 **Nexus Architect** analyzing codebase context...\n"
            
            # 2. Generate Report (Try Pro, Fallback to Flash)
            try:
                yield "⚡ Using **Gemini 2.5 Pro** for deep analysis...\n\n"
                for chunk in self.chain_pro.stream({"context": context_text}):
                    yield chunk
            except Exception as e:
                if "429" in str(e) or "ResourceExhausted" in str(e):
                    yield "\n\n⚠️ **Pro Quota Exceeded**. Switching to **Gemini 2.5 Flash** for high-speed audit...\n\n"
                    # Add delay to be safe?
                    import time
                    time.sleep(1)
                    for chunk in self.chain_flash.stream({"context": context_text}):
                        yield chunk
                else:
                    raise e
                
        except Exception as e:
            yield f"Error running audit: {str(e)}"

architect_agent = ArchitectAgent()
