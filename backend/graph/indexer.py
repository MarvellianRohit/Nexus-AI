import os
import glob
import json
import concurrent.futures
from pathlib import Path
from neo4j import GraphDatabase
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

# Configuration
PROJECT_ROOT = "/Users/rohitchandra/Documents"
PROJECT_DIRS = ["AI", "E-Commerce App", "Food Delivery App", "college"]
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "password123"
TEACHER_MODEL = "phi3:mini"
MAX_WORKERS = 1

class CodeGraphIndexer:
    def __init__(self):
        print(f"🔗 Connecting to Neo4j at {NEO4J_URI}...")
        self.driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
        print("🤖 Initializing LLM (phi3:mini)...")
        self.llm = ChatOllama(model=TEACHER_MODEL, temperature=0)
        self.parser = JsonOutputParser()
        
        self.extraction_prompt = ChatPromptTemplate.from_template("""
        Extract Entities and Relationships from code.
        
        File: {filename}
        Code: {code}
        
        Output valid JSON with "entities" and "relationships".
        """)

    def close(self):
        self.driver.close()

    def run_cypher(self, query, params=None):
        with self.driver.session() as session:
            session.run(query, params or {})

    def extract_from_file(self, file_path):
        import time
        max_retries = 1
        for attempt in range(max_retries + 1):
            try:
                filename = os.path.relpath(file_path, PROJECT_ROOT)
                print(f"📄 Processing {filename} (Attempt {attempt+1})...")
                
                with open(file_path, 'r', encoding='utf-8') as f:
                    code = f.read()
                
                code_snippet = code[:1500] 
                
                print(f"🧠 Prompting LLM for {filename}...")
                chain = self.extraction_prompt | self.llm
                raw_response = chain.invoke({"filename": filename, "code": code_snippet})
                print(f"📥 Received Response for {filename}: {str(raw_response.content)[:100]}...")
                
                data = self.parser.parse(raw_response.content)
                self.ingest_graph(filename, data)
                return f"✅ Indexed {filename}"
            except Exception as e:
                print(f"⚠️ Error in {file_path}: {e}")
                time.sleep(1)
        return f"❌ Failed {file_path}."

    def ingest_graph(self, filename, data):
        # 1. Ensure File Node
        self.run_cypher("MERGE (f:File {name: $name})", {"name": filename})
        
        # 2. Ingest Entities
        for entity in data.get("entities", []):
            label = entity.get("type", "Entity")
            name = entity.get("name")
            if name:
                self.run_cypher(
                    f"MERGE (e:{label} {{name: $name}}) MERGE (f:File {{name: $file}}) MERGE (f)-[:DEFINES]->(e)",
                    {"name": name, "file": filename}
                )
        
        # 3. Ingest Relationships
        for rel in data.get("relationships", []):
            source = rel.get("source")
            target = rel.get("target")
            rel_type = rel.get("type", "DEPENDS_ON")
            if source and target:
                self.run_cypher(
                    f"MERGE (s {{name: $source}}) MERGE (t {{name: $target}}) MERGE (s)-[:{rel_type}]->(t)",
                    {"source": source, "target": target}
                )

    def scan_and_index(self):
        # Target important file types
        extensions = ['*.ts', '*.tsx', '*.py', '*.js']
        files = []
        for pdir in PROJECT_DIRS:
            base_path = os.path.join(PROJECT_ROOT, pdir)
            print(f"🔍 Scanning {base_path}...")
            for ext in extensions:
                files.extend(glob.glob(os.path.join(base_path, "**", ext), recursive=True))
        
        # Filter out node_modules and big dirs
        files = [f for f in files if "node_modules" not in f and ".git" not in f and "dist" not in f and "venv" not in f]
        
        total = len(files)
        print(f"🚀 Found {total} files. Starting parallel extraction with {MAX_WORKERS} workers...")
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            futures = [executor.submit(self.extract_from_file, f) for f in files]
            count = 0
            for future in concurrent.futures.as_completed(futures):
                count += 1
                print(f"[{count}/{total}] {future.result()}")

if __name__ == "__main__":
    print("🚀 Initializing CodeGraphIndexer...")
    indexer = CodeGraphIndexer()
    print("✅ Indexer Initialized. Starting Scan...")
    try:
        indexer.scan_and_index()
    finally:
        indexer.close()
        print("🏁 Indexing Sequence Finished.")
