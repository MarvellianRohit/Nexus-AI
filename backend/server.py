from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uvicorn
import asyncio
import os

# Import backend modules
from backend.rag import rag_service
from backend.ingest import ingest_documents
from backend.agents.workflow import run_feature_workflow
from backend.vision import generate_code_from_image
from backend.search_service import search_service
from backend.architect.agent import architect_agent
from backend.architect.ingest import ingest_codebase

# --- Data Models (Must be defined before use) ---
class ChatRequest(BaseModel):
    message: str

class AgentRequest(BaseModel):
    feature: str

# --- App Initialization ---
app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static Files (Social Media Assets)
os.makedirs("backend/static/social", exist_ok=True)
app.mount("/static/social", StaticFiles(directory="backend/static/social"), name="social")

# --- Routes ---

@app.get("/")
def read_root():    
    return {"status": "Nexus-AI Server Running"}

# 1. RAG Chat (Deep Research)
@app.post("/api/chat")
async def chat(request: ChatRequest):
    async def generate():
        try:
            for chunk in rag_service.query(request.message):
                yield chunk
        except Exception as e:
            yield f"Error: {str(e)}"

    return StreamingResponse(generate(), media_type="text/plain")

# 2. General Assistant (Gemini Pro)
@app.post("/api/general/chat")
async def general_chat(request: ChatRequest):
    async def generate():
        try:
            # Using Gemini Pro Service
            for chunk in search_service.chat_stream(request.message):
                yield chunk
        except Exception as e:
            yield f"Error: {str(e)}"

    return StreamingResponse(generate(), media_type="text/plain")

# 3. RAG Ingest
@app.post("/api/ingest")
async def ingest():
    try:
        result = ingest_documents()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 4. Agent Workforce
@app.post("/api/agents/generate")
async def generate_agent(request: AgentRequest):
    async def run_workflow():
        try:
            # We wrap the synchronous CrewAI/Lite call
            result = run_feature_workflow(request.feature)
            yield f"Workflow Complete: {result}"
        except Exception as e:
            yield f"Error: {str(e)}"

    return StreamingResponse(run_workflow(), media_type="text/plain")

# 5. Vision Projector
@app.post("/api/vision/generate")
async def vision_generate(file: UploadFile = File(...)):
    async def process_vision():
        try:
            contents = await file.read()
            # Stream the response from the vision model
            for chunk in generate_code_from_image(contents):
                yield chunk
        except Exception as e:
            yield f"Error: {str(e)}"

    return StreamingResponse(process_vision(), media_type="text/plain")

    return StreamingResponse(process_vision(), media_type="text/plain")

# 6. Nexus Architect
@app.post("/api/architect/ingest")
async def architect_ingest_route():
    try:
        result = ingest_codebase()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/architect/audit")
async def architect_audit_route():
    async def generate_report():
        try:
            for chunk in architect_agent.run_audit():
                yield chunk
        except Exception as e:
            yield f"Error: {str(e)}"
            
    return StreamingResponse(generate_report(), media_type="text/plain")

# 7. Nexus Researcher
class ResearchRequest(BaseModel):
    query: str

@app.post("/api/researcher/run")
async def run_research(request: ResearchRequest):
    """
    Executes the Nexus Researcher agent.
    """
    # Lazy import to avoid potential circular dependency issues during startup
    from backend.researcher.agent import run_researcher
    try:
        report = run_researcher(request.query)
        return {"status": "success", "report": report}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# 8. Nexus Creator (Video based Blog)
@app.post("/api/creator/upload")
async def creator_upload(file: UploadFile = File(...)):
    """
    Processes a video file: Transcribe (Whisper) -> Blog (Llama-3).
    """
    import shutil
    from backend.creator.transcribe import transcribe_video
    from backend.creator.blog_generator import generate_blog_post, save_to_docs

    try:
        # 1. Save File
        upload_dir = "uploads"
        os.makedirs(upload_dir, exist_ok=True)
        file_location = f"{upload_dir}/{file.filename}"
        
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # 2. Transcribe
        transcription = transcribe_video(file_location)
        
        # 3. Generate Blog
        blog_content = generate_blog_post(transcription)
        
        # 4. Save to /docs
        saved_path = save_to_docs(blog_content, filename=f"blog_{file.filename}.md")
        
        return {
            "status": "success", 
            "transcription": transcription[:500] + "...", 
            "blog_content": blog_content,
            "saved_path": saved_path
        }
    except Exception as e:
        return {"status": "error", "message": f"Creator Flow Failed: {str(e)}"}

# 9. Graph-RAG Impact Analysis
class GraphRequest(BaseModel):
    question: str

@app.post("/api/graph/impact")
async def graph_impact_route(request: GraphRequest):
    """
    Analyzes system impact using Neo4j Knowledge Graph.
    """
    from backend.graph.query import GraphRAG
    rag = GraphRAG()
    try:
        answer = rag.run_query(request.question)
        return {"status": "success", "answer": answer}
    except Exception as e:
        return {"status": "error", "message": f"Graph Query Failed: {str(e)}"}
    finally:
        rag.close()

# 10. Autonomous Social Media Agent
class SocialRequest(BaseModel):
    feature_desc: str

@app.post("/api/agents/social")
async def social_agent_route(request: SocialRequest):
    """
    Generates multi-modal social media content via SDXL, Whisper, and Llama-3.
    """
    from backend.agents.social_media import SocialMediaAgent
    agent = SocialMediaAgent()
    try:
        results = agent.run_autonomous_flow(request.feature_desc)
        return {"status": "success", "results": results}
    except Exception as e:
        return {"status": "error", "message": f"Social Agent Failed: {str(e)}"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
