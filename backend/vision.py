import base64
import io
from PIL import Image
from langchain_community.chat_models import ChatOllama
from langchain.schema import HumanMessage

# Configuration
# 'llava' is the standard tag. User can pull 'llava:34b' and tag it as 'llava' 
# or change this constant. 'moondream' is also a good fast option.
VISION_MODEL = "llava" 

def encode_image(image_file):
    """Encodes an image file to base64 string."""
    return base64.b64encode(image_file.read()).decode('utf-8')

def analyze_image_stream(image_bytes, prompt="Describe this image"):
    """
    Analyzes an image using Ollama's vision model and streams the response.
    """
    try:
        # Validate image using Pillow
        img = Image.open(io.BytesIO(image_bytes))
        
        # Re-encode to ensure valid format and possibly resize if huge
        # (Ollama handles large images well, but let's be safe if it's massive)
        img.thumbnail((1920, 1920)) 
        buffered = io.BytesIO()
        img.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")

        llm = ChatOllama(model=VISION_MODEL, base_url="http://localhost:11434")
        
        message = HumanMessage(
            content=[
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": f"data:image/png;base64,{img_str}"},
            ]
        )
        
        for chunk in llm.stream([message]):
            yield chunk.content

    except Exception as e:
        yield f"Error processing image: {str(e)}"

def generate_code_from_image(image_bytes):
    """
    Designer Agent: Extracts tokens and code.
    """
    prompt = """
    You are an expert UI/UX Designer and Frontend Developer. 
    Analyze this UI screenshot.
    
    PART 1: Design Tokens
    First, list the key design attributes you see:
    - Primary Colors (Hex codes)
    - Font Family suggestions
    - Spacing (Padding/Margin estimates in Tailwind classes, e.g. p-4, p-8)
    - Border Radius (rounded-lg, rounded-full, etc.)
    
    PART 2: Implementation
    Write the full React/Next.js code to replicate the UI.
    
    Requirements:
    1. Use 'lucide-react' for icons.
    2. Use 'Tailwind CSS' for styling.
    3. Make it fully responsive (mobile-first).
    4. Use standard HTML elements (div, button, input).
    5. Return ONLY the code (and the tokens in comments at the top).
    """
    
    return analyze_image_stream(image_bytes, prompt)
