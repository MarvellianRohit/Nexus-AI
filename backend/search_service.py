from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

# Configuration
GOOGLE_API_KEY = "AIzaSyB0XcmiVCVDen-Qk0pwgadEiN2aAUGLkKU"

class GeneralSearchService:
    def __init__(self):
        # Primary: Gemini 2.5 Pro (Power)
        self.llm_pro = ChatGoogleGenerativeAI(
            model="gemini-2.5-pro", 
            google_api_key=GOOGLE_API_KEY,
            convert_system_message_to_human=True,
            max_retries=1  # Fail fast to switch to Flash
        )
        
        # Fallback: Gemini 2.5 Flash (Speed/Reliability)
        self.llm_flash = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash", 
            google_api_key=GOOGLE_API_KEY,
            convert_system_message_to_human=True
        )

        # System Prompts
        self.prompt_pro = ChatPromptTemplate.from_template("""You are an advanced, highly intelligent AI. Analyze the user's question deeply. Provide a comprehensive, insightful, and well-structured answer. Explain your reasoning.

Question: {question}

Detailed Answer:""")

        self.prompt_flash = ChatPromptTemplate.from_template("""Answer the user's question directly and concisely.

Question: {question}

Answer:""")

    def chat_stream(self, user_message: str):
        """
        Try Pro -> Fallback to Flash
        """
        try:
            # Try Pro Model
            # Note: We manually stream to catch errors early if possible, 
            # though streaming might yield some tokens before failing. 
            # For robustness, we'll try/except the stream generator.
            
            chain_pro = self.prompt_pro | self.llm_pro | StrOutputParser()
            
            # We use a generator to yield tokens, but if it fails immediately we catch it.
            # Using a flag to track if we successfully started streaming
            started = False
            try:
                for chunk in chain_pro.stream({"question": user_message}):
                    started = True
                    yield chunk
            except Exception as e:
                # If we already sent data, we can't cleanly switch context easily in this stream,
                # but we can append a message. If we haven't sent anything, we switch entirely.
                if not started:
                    raise e # Re-raise to trigger fallback
                else:
                    yield f"\n\n[System: Pro model error ({str(e)}). Switching to Flash for future queries.]"
                    
        except Exception as e:
            # Fallback to Flash
            yield "⚡ Pro busy, switching to Flash...\n\n"
            chain_flash = self.prompt_flash | self.llm_flash | StrOutputParser()
            for chunk in chain_flash.stream({"question": user_message}):
                yield chunk

search_service = GeneralSearchService()
