import os
import json
import random
from langchain_chroma import Chroma
from langchain_ollama import ChatOllama
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# Configuration
CHROMA_PATH = "chroma_db"
COLLECTION_NAME = "nexus_architect"
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
OUTPUT_FILE = "backend/distillation/data/golden_dataset.jsonl"
TEACHER_MODEL = "llama3:70b"

def ensure_directory():
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

def get_local_code_samples(k=250):
    """
    Retrieves random code snippets from ChromaDB.
    """
    print("🔍 Retrieving local code samples...")
    try:
        embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)
        vector_store = Chroma(
            collection_name=COLLECTION_NAME,
            embedding_function=embeddings,
            persist_directory=CHROMA_PATH
        )
        # Fetch all IDs (hacky retrieval of raw data, realistically we query generic terms)
        results = vector_store.similarity_search("function class component", k=k)
        return [doc.page_content for doc in results]
    except Exception as e:
        print(f"⚠️ ChromaDB Retrieval Failed: {e}. Using synthetic fallback.")
        return []

def generate_synthetic_prompts(n=250):
    """
    Returns a list of synthetic coding challenges.
    """
    topics = ["Recursion", "Dynamic Programming", "API Rate Limiting", "React Hooks", "Database Indexing", "Async/Await", "Systems Design"]
    prompts = []
    for _ in range(n):
        topic = random.choice(topics)
        prompts.append(f"Write a comprehensive guide and code solution for a complex problem involving {topic}.")
    return prompts

def generate_golden_dataset():
    ensure_directory()
    
    # 1. Gather Inputs
    local_code = get_local_code_samples(k=250)
    synthetic_prompts = generate_synthetic_prompts(n=500 - len(local_code))
    
    inputs = []
    
    # Format Local Code as "Refactor/Optimize" tasks
    for code in local_code:
        inputs.append(f"Analyze this code and rewrite it with perfect type safety, error handling, and documentation:\n\n{code[:2000]}") # Truncate to avoid context overflow
        
    inputs.extend(synthetic_prompts)
    
    print(f"🚀 Starting Distillation. Teacher: {TEACHER_MODEL}. Inputs: {len(inputs)}")
    
    # 2. Teacher Loop
    llm = ChatOllama(model=TEACHER_MODEL, temperature=0.7)
    
    with open(OUTPUT_FILE, "a") as f:
        for i, prompt_text in enumerate(inputs):
            print(f"Generating sample {i+1}/{len(inputs)}...")
            try:
                # Chain of Thought Prompt
                system_prompt = """You are an Elite Software Architect.
                Generate a perfect, production-ready solution.
                Include:
                1. Deep explanation of the implementation strategy.
                2. The Code (Type-Safe, Commented, Efficient).
                3. Complexity Analysis (Time/Space).
                """
                
                messages = [
                    ("system", system_prompt),
                    ("human", prompt_text),
                ]
                
                response = llm.invoke(messages)
                
                # Format for MLX Training (Chat format)
                entry = {
                    "messages": [
                        {"role": "user", "content": prompt_text},
                        {"role": "assistant", "content": response.content}
                    ]
                }
                
                f.write(json.dumps(entry) + "\n")
                f.flush() # Ensure save
                
            except Exception as e:
                print(f"❌ Generation failed for sample {i}: {e}")

if __name__ == "__main__":
    generate_golden_dataset()
