from neo4j import GraphDatabase
import os
import json

NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password123")
LOCAL_GRAPH_PATH = "/Users/rohitchandra/Documents/AI/backend/graph/local_cache.json"

class KnowledgeGraph:
    def __init__(self):
        self.driver = None
        self.local_mode = False
        try:
            self.driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
            self.driver.verify_connectivity()
            print("✅ Using Neo4j Graph Database.")
        except Exception:
            print("⚠️ Neo4j unavailable. Using local JSON graph fallback.")
            self.local_mode = True
            self.local_data = self._load_local()

    def _load_local(self):
        if os.path.exists(LOCAL_GRAPH_PATH):
            with open(LOCAL_GRAPH_PATH, "r") as f:
                return json.load(f)
        return {"nodes": {}, "edges": []}

    def _save_local(self):
        with open(LOCAL_GRAPH_PATH, "w") as f:
            json.dump(self.local_data, f, indent=2)

    def close(self):
        if self.driver: self.driver.close()

    def query(self, cypher_query, params=None):
        if self.local_mode: return [] # Local mode doesn't support complex Cypher yet
        with self.driver.session() as session:
            result = session.run(cypher_query, params or {})
            return [data.data() for data in result]

    def ingest_local_relationship(self, src, tgt, rtype):
        if not self.local_mode: return
        self.local_data["edges"].append({"source": src, "target": tgt, "type": rtype})
        self._save_local()

    def get_dependencies(self, entity_name):
        if self.local_mode:
            return [{"name": e["target"], "type": e["type"]} for e in self.local_data["edges"] if e["source"] == entity_name]
        query = """
        MATCH (e {name: $name})-[:CALLS|IMPORTS|DEPENDS_ON|INHERITS]*->(dep)
        RETURN dep.name as name, labels(dep)[0] as type
        """
        return self.query(query, {"name": entity_name})

    def get_impact(self, entity_name):
        if self.local_mode:
            return [{"name": e["source"], "type": e["type"]} for e in self.local_data["edges"] if e["target"] == entity_name]
        query = """
        MATCH (imp)-[:CALLS|IMPORTS|DEPENDS_ON|INHERITS]*->(e {name: $name})
        RETURN imp.name as name, labels(imp)[0] as type
        """
        return self.query(query, {"name": entity_name})

    def get_definition_file(self, entity_name):
        query = """
        MATCH (f:File)-[:DEFINES]->(e {name: $name})
        RETURN f.path as path
        """
        return self.query(query, {"name": entity_name})

kg_service = KnowledgeGraph()
