import os
from typing import TypedDict, List, Annotated
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, SystemMessage, BaseMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# --- Configuration ---
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY") or "AIzaSyB0XcmiVCVDen-Qk0pwgadEiN2aAUGLkKU"
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

if not TAVILY_API_KEY:
    print("⚠️ Tavily API Key missing. Researcher will fail.")

# --- LLM Setup ---
if not GOOGLE_API_KEY:
    print("⚠️ GOOGLE_API_KEY missing. Researcher analysis will fail.")

llm_pro = ChatGoogleGenerativeAI(
    model="gemini-2.5-pro",
    google_api_key=GOOGLE_API_KEY,
    convert_system_message_to_human=True,
    temperature=0.2,
    max_retries=0 # Fail fast
)

llm_flash = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=GOOGLE_API_KEY,
    convert_system_message_to_human=True,
    temperature=0.2
)

# --- State Design ---
class ResearcherState(TypedDict):
    query: str
    search_results: str
    analysis: str
    migration_plan: str
    messages: List[BaseMessage]

# --- Nodes ---

def search_node(state: ResearcherState):
    """
    Searches the web using Tavily (Primary) or DuckDuckGo (Fallback).
    """
    query = state["query"]
    print(f"🌍 Researcher: Searching for '{query}'...")
    
    try:
        if TAVILY_API_KEY:
            # Primary: Tavily
            search_tool = TavilySearchResults(max_results=5)
            results = search_tool.invoke(query)
            context = "\\n".join([f"- [{r['url']}]: {r['content']}" for r in results])
            return {"search_results": context}
        else:
            # Fallback: DuckDuckGo
            from langchain_community.tools import DuckDuckGoSearchRun
            print("⚠️ Tavily Key missing. Using DuckDuckGo Fallback.")
            search_tool = DuckDuckGoSearchRun()
            # DDG returns a string directly usually, or we wrap it
            results = search_tool.invoke(query)
            return {"search_results": f"DuckDuckGo Results:\\n{results}"}
            
    except Exception as e:
        return {"search_results": f"Search Failed: {str(e)}"}

def analyze_node(state: ResearcherState):
    """
    Compares search findings with generic codebase knowledge (package.json).
    """
    print("🧠 Researcher: Analyzing findings...")
    query = state["query"]
    results = state["search_results"]
    
    # Read package.json for context
    try:
        with open("package.json", "r") as f:
            package_json = f.read()
    except:
        package_json = "No package.json found."
    
    prompt = ChatPromptTemplate.from_template("""You are a Senior Technical Researcher.
    
    User Query: {query}
    
    Current Project Definition (package.json):
    {package_json}
    
    Latest Web Findings:
    {results}
    
    Task:
    Analyze these findings. Identify the key technical patterns, best practices, and major changes (breaking changes) introduced in these new technologies.
    Contrast this with the current project dependencies found in package.json (e.g. current Next.js version vs latest).
    
    Output a concise analysis.
    """)
    
    chain_pro = prompt | llm_pro | StrOutputParser()
    chain_flash = prompt | llm_flash | StrOutputParser()
    
    try:
        analysis = chain_pro.invoke({"query": query, "results": results, "package_json": package_json})
    except Exception as e:
        print(f"⚠️ Pro Model Failed (Analyze): {e}. Switching to Flash.")
        analysis = chain_flash.invoke({"query": query, "results": results, "package_json": package_json})
        
    return {"analysis": analysis}

def plan_node(state: ResearcherState):
    """
    Proposes a migration plan based on the analysis.
    """
    print("📋 Researcher: Drafting migration plan...")
    analysis = state["analysis"]
    
    prompt = ChatPromptTemplate.from_template("""You are a Software Architect.
    
    Research Analysis:
    {analysis}
    
    Task:
    Propose a concrete 'Migration Plan' to update a project to these new standards.
    Structure it as:
    1. Executive Summary
    2. Key Changes Required
    3. Step-by-Step Migration Strategy
    4. Pitfalls to Avoid
    
    Format as Markdown.
    """)
    
    chain_pro = prompt | llm_pro | StrOutputParser()
    chain_flash = prompt | llm_flash | StrOutputParser()
    
    try:
        plan = chain_pro.invoke({"analysis": analysis})
    except Exception as e:
        print(f"⚠️ Pro Model Failed (Plan): {e}. Switching to Flash.")
        plan = chain_flash.invoke({"analysis": analysis})
        
    return {"migration_plan": plan}

# --- Graph Definition ---
workflow = StateGraph(ResearcherState)

workflow.add_node("search", search_node)
workflow.add_node("analyze", analyze_node)
workflow.add_node("plan", plan_node)

workflow.set_entry_point("search")
workflow.add_edge("search", "analyze")
workflow.add_edge("analyze", "plan")
workflow.add_edge("plan", END)

app = workflow.compile()

def run_researcher(query: str):
    """
    Entry point for the API.
    """
    initial_state = {"query": query, "messages": [HumanMessage(content=query)]}
    result = app.invoke(initial_state)
    return result["migration_plan"]
