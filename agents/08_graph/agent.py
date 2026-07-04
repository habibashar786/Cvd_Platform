"""
AGENT 8 - Graph Intelligence Agent
Builds a UMLS-aligned cardiovascular risk factor knowledge graph
and provides utilities to retrieve clinical terms and relations.
"""
from pathlib import Path
import json
from datetime import datetime, timezone
import networkx as nx

OUTPUT_DIR = Path("outputs/08_graph_rag")
GRAPH_JSON = OUTPUT_DIR / "knowledge_graph.json"

def build_graph() -> nx.DiGraph:
    G = nx.DiGraph()
    
    # Add Nodes with clinical concept definitions (UMLS codes or descriptions)
    nodes = {
        "Age": {"type": "demographic", "desc": "Patient age in years"},
        "Gender": {"type": "demographic", "desc": "Patient physiological gender"},
        "Systolic_BP": {"type": "vital", "desc": "Systolic blood pressure (ap_hi)"},
        "Diastolic_BP": {"type": "vital", "desc": "Diastolic blood pressure (ap_lo)"},
        "Pulse_Pressure": {"type": "derived_vital", "desc": "Difference between systolic and diastolic BP"},
        "Cholesterol": {"type": "lab", "desc": "Total blood cholesterol level"},
        "Glucose": {"type": "lab", "desc": "Blood glucose level"},
        "BMI": {"type": "derived_demographic", "desc": "Body Mass Index calculated from weight and height"},
        "Smoking": {"type": "lifestyle", "desc": "Active tobacco smoking status"},
        "Alcohol": {"type": "lifestyle", "desc": "Alcohol consumption status"},
        "Active_Lifestyle": {"type": "lifestyle", "desc": "Level of physical activity status"},
        "CVD_Risk": {"type": "clinical_outcome", "desc": "10-year risk of cardiovascular disease event"},
        "Hypertension": {"type": "diagnosis", "desc": "High blood pressure condition (BP >= 140/90)"},
        "Arterial_Stiffness": {"type": "pathology", "desc": "Loss of arterial compliance and elasticity"},
        "Hypercholesterolemia": {"type": "diagnosis", "desc": "Abnormally high levels of cholesterol in the blood"}
    }
    
    for node, attrs in nodes.items():
        G.add_node(node, **attrs)
        
    # Add Directed Edges mapping clinical relationships (causality and associations)
    edges = [
        ("Age", "Systolic_BP", "increases_with"),
        ("Age", "Arterial_Stiffness", "causes_gradual"),
        ("Smoking", "Arterial_Stiffness", "accelerates"),
        ("Smoking", "CVD_Risk", "directly_increases"),
        ("Arterial_Stiffness", "Systolic_BP", "increases"),
        ("Systolic_BP", "Pulse_Pressure", "increases"),
        ("Diastolic_BP", "Pulse_Pressure", "decreases"),
        ("Systolic_BP", "Hypertension", "defines"),
        ("Diastolic_BP", "Hypertension", "defines"),
        ("Cholesterol", "Hypercholesterolemia", "defines"),
        ("Hypercholesterolemia", "Arterial_Stiffness", "promotes_plaque"),
        ("Glucose", "CVD_Risk", "induces_endothelial_damage"),
        ("Hypertension", "CVD_Risk", "increases_strain"),
        ("Active_Lifestyle", "CVD_Risk", "reduces_risk"),
        ("Active_Lifestyle", "Systolic_BP", "lowers"),
        ("Alcohol", "Systolic_BP", "increases_if_excessive")
    ]
    
    for u, v, rel in edges:
        G.add_edge(u, v, relationship=rel)
        
    return G

def get_related_nodes(term: str) -> list[dict]:
    """Retrieve connected terms and their clinical relationships from the graph."""
    G = build_graph()
    normalized = term.lower().strip()
    
    # Map input queries to graph node keys
    mapping = {
        "bp": "Systolic_BP",
        "blood pressure": "Systolic_BP",
        "systolic": "Systolic_BP",
        "diastolic": "Diastolic_BP",
        "cholesterol": "Cholesterol",
        "lipid": "Cholesterol",
        "glucose": "Glucose",
        "sugar": "Glucose",
        "smoking": "Smoking",
        "smoke": "Smoking",
        "active": "Active_Lifestyle",
        "exercise": "Active_Lifestyle",
        "age": "Age",
        "weight": "BMI",
        "bmi": "BMI"
    }
    
    node_key = None
    for k, v in mapping.items():
        if k in normalized:
            node_key = v
            break
            
    if not node_key or not G.has_node(node_key):
        # Fallback: check direct node name match
        for n in G.nodes():
            if n.lower() in normalized:
                node_key = n
                break
                
    if not node_key:
        return []
        
    results = []
    # Add attributes of the node itself
    results.append({
        "term": node_key,
        "role": "subject",
        "type": G.nodes[node_key].get("type"),
        "description": G.nodes[node_key].get("desc")
    })
    
    # Outgoing relationships
    for succ in G.successors(node_key):
        results.append({
            "term": succ,
            "role": "target",
            "relationship": G.edges[node_key, succ].get("relationship"),
            "description": G.nodes[succ].get("desc")
        })
        
    # Incoming relationships
    for pred in G.predecessors(node_key):
        results.append({
            "term": pred,
            "role": "source",
            "relationship": G.edges[pred, node_key].get("relationship"),
            "description": G.nodes[pred].get("desc")
        })
        
    return results

def run() -> dict:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    try:
        G = build_graph()
        
        # Serialize NetworkX Graph into a compatible Node-Link format
        # compatible with JSON uploader
        nodes_list = []
        for n in G.nodes():
            nodes_list.append({
                "id": n,
                "type": G.nodes[n].get("type"),
                "desc": G.nodes[n].get("desc")
            })
            
        edges_list = []
        for u, v in G.edges():
            edges_list.append({
                "source": u,
                "target": v,
                "relationship": G.edges[u, v].get("relationship")
            })
            
        data = {
            "nodes": nodes_list,
            "edges": edges_list,
            "node_count": len(nodes_list),
            "edge_count": len(edges_list),
            "generated_at": datetime.now(timezone.utc).isoformat()
        }
        
        GRAPH_JSON.write_text(json.dumps(data, indent=2))
        return {"success": True, "artifact": str(GRAPH_JSON)}
    except Exception as e:
        return {"success": False, "error": str(e), "artifact": ""}

if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
