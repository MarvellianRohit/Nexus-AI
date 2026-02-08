from neo4j import GraphDatabase
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# Configuration
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "password123"
TEACHER_MODEL = "llama3:70b"

class GraphRAG:
    def __init__(self):
        self.driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
        self.llm = ChatOllama(model=TEACHER_MODEL, temperature=0.1)
        
        self.cypher_prompt = ChatPromptTemplate.from_template("""
        You are an expert Neo4j developer. Convert the following natural language question into a VALID Cypher query.
        
        Schema:
        - Node Labels: File, Function, Class, Variable, Component, Entity
        - Relationships: DEFINES, CALLS, IMPORTS, DEPENDS_ON, IMPLEMENTS
        - Properties: name (string)
        
        Rules:
        1. Use simple relationship patterns like (n)-[*..3]-(m) for impact tracing.
        2. Always use `CONTAINS` or `DISTINCT` for name searches if the exact name is unknown.
        3. Do not use specialized functions like `shortestPath` unless explicitly required.
        4. Return nodes and their relationships.
        
        Question: {question}
        
        Output ONLY the Cypher query text.
        """)

        self.answer_prompt = ChatPromptTemplate.from_template("""
        You are a Senior System Architect. Based on the following graph data retrieved from the codebase, answer the user's question about system impact and architecture.
        
        User Question: {question}
        Graph Data: {data}
        
        Provide a detailed technical explanation of the impacts, dependencies, and potential risks.
        """)

    def close(self):
        self.driver.close()

    def run_query(self, question):
        try:
            # 1. Generate Cypher
            cypher_chain = self.cypher_prompt | self.llm | StrOutputParser()
            cypher_query = cypher_chain.invoke({"question": question})
            
            # Clean Markdown formatting if present
            cypher_query = cypher_query.replace("```cypher", "").replace("```", "").strip()
            print(f"🔍 Generated Cypher: {cypher_query}")
            
            # 2. Execute Cypher
            with self.driver.session() as session:
                result = session.run(cypher_query)
                data = [record.data() for record in result]
            
            # 3. Generate Natural Language Answer
            answer_chain = self.answer_prompt | self.llm | StrOutputParser()
            answer = answer_chain.invoke({"question": question, "data": str(data)})
            return answer
            
        except Exception as e:
            return f"❌ Graph-RAG Error: {e}"

if __name__ == "__main__":
    rag = GraphRAG()
    try:
        # Example test
        q = "Wait, let's wait for actual indexing. This is just for structural check."
        # print(rag.run_query("What happens if I change the Auth logic?"))
    finally:
        rag.close()
