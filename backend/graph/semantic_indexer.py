import os
import glob
import json
import concurrent.futures
from pathlib import Path
from neo4j import GraphDatabase
from backend.mlx_engine import mlx_engine
from backend.graph.knowledge_graph import kg_service

# Configuration
PROJECT_ROOT = "/Users/rohitchandra/Documents/AI"
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password123")
# Leverage 16 cores for relationship extraction
MAX_WORKERS = os.cpu_count() or 16

class SemanticIndexer:
    def __init__(self):
        self.driver = None
        try:
            self.driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
            # Test connection
            self.driver.verify_connectivity()
            print("✅ Connected to Neo4j.")
        except Exception as e:
            print(f"⚠️ Neo4j Connection Failed: {e}. Indexing will skip graph updates.")

        self.extraction_prompt = """You are a Semantic Code Analyzer.
Analyze the following code from file: {filename}
Code:
{code}

Extract:
1. **Entities**: (Classes, Functions, Interfaces, Components)
2. **Relationships**: (Inherits, Calls, Imports, DependsOn)

Return ONLY valid JSON:
{{
  "entities": [{{ "name": "...", "type": "...", "description": "..." }}],
  "relationships": [{{ "source": "...", "target": "...", "type": "..." }}]
}}
"""

    def close(self):
        if self.driver:
            self.driver.close()

    def run_cypher(self, query, params=None):
        if not self.driver: return
        with self.driver.session() as session:
            session.run(query, params or {})

    def process_file(self, file_path):
        try:
            filename = os.path.relpath(file_path, PROJECT_ROOT)
            with open(file_path, 'r', encoding='utf-8') as f:
                code = f.read()

            # Analyze first 4000 characters for high-level structure
            analysis_prompt = self.extraction_prompt.format(filename=filename, code=code[:4000])
            
            # Use Llama-3-70B for high-fidelity extraction
            raw_response = mlx_engine.generate_response(analysis_prompt, model_key="reasoning")
            
            # Clean response for JSON parsing
            json_match = re.search(r'\{.*\}', raw_response, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                self.ingest_data(filename, data)
                return f"✅ Indexed {filename}"
            return f"⚠️ No JSON found in {filename}"
        except Exception as e:
            return f"❌ Error in {file_path}: {str(e)}"

    def ingest_data(self, filename, data):
        # File Node
        if self.driver:
            self.run_cypher("MERGE (f:File {path: $path})", {"path": filename})
        
        for entity in data.get("entities", []):
            etype = entity.get("type", "Component")
            ename = entity.get("name")
            if ename:
                if self.driver:
                    self.run_cypher(
                        f"MERGE (e:{etype} {{name: $name}}) "
                        "WITH e "
                        "MATCH (f:File {path: $path}) "
                        "MERGE (f)-[:DEFINES]->(e)",
                        {"name": ename, "path": filename}
                    )
                # Note: local DEFINES is implicitly handled by the graph structure if needed

        for rel in data.get("relationships", []):
            src = rel.get("source")
            tgt = rel.get("target")
            rtype = rel.get("type", "DEPENDS_ON").replace(" ", "_").upper()
            if src and tgt:
                if self.driver:
                    self.run_cypher(
                        f"MERGE (s {{name: $src}}) "
                        f"MERGE (t {{name: $tgt}}) "
                        f"MERGE (s)-[:{rtype}]->(t)",
                        {"src": src, "tgt": tgt}
                    )
                else:
                    kg_service.ingest_local_relationship(src, tgt, rtype)

    def run(self):
        extensions = ["**/*.py", "**/*.ts", "**/*.tsx", "**/*.js", "**/*.c", "**/*.cpp"]
        files = []
        for ext in extensions:
            files.extend(glob.glob(os.path.join(PROJECT_ROOT, ext), recursive=True))
        
        # Exclude common noise
        files = [f for f in files if all(noise not in f for noise in ["node_modules", ".next", ".git", "venv", "dist"])]
        
        print(f"🚀 Found {len(files)} files. Starting extraction with {MAX_WORKERS} cores...")
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            list(executor.map(self.process_file, files))
        
        print("🏁 Semantic Indexing Complete.")

if __name__ == "__main__":
    import re
    indexer = SemanticIndexer()
    try:
        indexer.run()
    finally:
        indexer.close()
