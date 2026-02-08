from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import os

def generate_blog_post(transcription: str, model: str = "llama3") -> str:
    """
    Generates a technical blog post from transcription using Llama-3 (via Ollama).
    """
    print(f"✍️ Nexus Creator: Generating blog using {model}...")
    
    try:
        # Check if Ollama is reachable (basic check, could be improved)
        # Using langchain_ollama
        llm = ChatOllama(model=model, temperature=0.7)
        
        prompt = ChatPromptTemplate.from_template("""You are an expert Technical Content Creator.
        
        Source Transcription:
        {transcription}
        
        Task:
        Turn this raw transcription into a high-quality Technical Blog Post.
        
        Requirements:
        1. Catchy Title.
        2. Introduction summarizing the video content.
        3. Key Takeaways (bullet points).
        4. Detailed Technical Explanation (with code snippets if mentioned/inferred).
        5. Conclusion.
        
        Format as Markdown.
        """)
        
        chain = prompt | llm | StrOutputParser()
        blog_post = chain.invoke({"transcription": transcription})
        return blog_post
        
    except Exception as e:
        return f"Blog Generation Failed: {str(e)}"

def save_to_docs(content: str, filename: str = "video_blog.md"):
    """
    Saves the generated content to the /docs folder.
    """
    docs_dir = os.path.join(os.getcwd(), "docs")
    os.makedirs(docs_dir, exist_ok=True)
    file_path = os.path.join(docs_dir, filename)
    
    with open(file_path, "w") as f:
        f.write(content)
        
    print(f"💾 Saved blog post to: {file_path}")
    return file_path
