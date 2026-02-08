from neo4j import GraphDatabase
import time

URI = "bolt://localhost:7687"
USER = "neo4j"
PASSWORD = "password123"

def test_conn():
    print(f"🔗 Attempting connection to {URI}...")
    start = time.time()
    try:
        driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))
        with driver.session() as session:
            result = session.run("RETURN 1 as n")
            record = result.single()
            print(f"✅ Connection Successful! Result: {record['n']}")
        driver.close()
    except Exception as e:
        print(f"❌ Connection Failed: {e}")
    print(f"⏱️ Elapsed: {time.time() - start:.2f}s")

if __name__ == "__main__":
    test_conn()
