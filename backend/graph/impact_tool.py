from backend.graph.knowledge_graph import kg_service
import json

def analyze_impact(entity_name: str):
    """
    Analyzes the impact of changing a specific code entity (Class, Function, etc.)
    by traversing the relationship graph.
    """
    print(f"🔍 Analyzing impact for: {entity_name}")
    
    # 1. Find Definition
    def_file = kg_service.get_definition_file(entity_name)
    file_path = def_file[0]['path'] if def_file else "Unknown"
    
    # 2. Find Upstream Dependencies (What uses this?)
    impacted = kg_service.get_impact(entity_name)
    
    # 3. Find Downstream Dependencies (What does this use?)
    dependencies = kg_service.get_dependencies(entity_name)
    
    # 4. Generate Report
    report = {
        "entity": entity_name,
        "defined_in": file_path,
        "impact_score": len(impacted),
        "risky_areas": [item['name'] for item in impacted][:10],
        "dependency_count": len(dependencies),
        "status": "DANGER" if len(impacted) > 5 else "STABLE"
    }
    
    return report

if __name__ == "__main__":
    # Test with a placeholder
    sample_report = analyze_impact("UserSecret")
    print(json.dumps(sample_report, indent=2))
