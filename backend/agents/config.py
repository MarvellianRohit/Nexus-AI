import os
from langchain_community.chat_models import ChatOllama

# Configure Ollama as the LLM for agents
# User should pull 'deepseek-coder-v2' or 'llama3:70b'
# defaulting to 'llama3' for safety, but user can change this
MODEL_NAME = "llama3" 

def get_llm():
    base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    # Increase timeout for large models
    return ChatOllama(model=MODEL_NAME, base_url=base_url, timeout=300)
