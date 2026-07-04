import sys
import importlib

# Register aliases for agents to allow tests to import modules with leading digits
agent_mappings = {
    "agents.agent_01_discovery": "agents.01_discovery",
    "agents.agent_02_cleaning": "agents.02_cleaning",
    "agents.agent_03_preprocessing": "agents.03_preprocessing",
    "agents.agent_04_eda": "agents.04_eda",
    "agents.agent_05_statistics": "agents.05_statistics",
    "agents.agent_06_ml": "agents.06_ml",
    "agents.agent_07_xai": "agents.07_xai",
    "agents.agent_08_graph": "agents.08_graph",
    "agents.agent_09_vector": "agents.09_vector",
    "agents.agent_10_rag": "agents.10_rag",
    "agents.agent_11_security": "agents.11_security",
    "agents.agent_12_deployment": "agents.12_deployment",
    "agents.agent_13_guardrail": "agents.13_guardrail",
    "agents.agent_14_qc": "agents.14_qc",
    "agents.agent_15_codereview": "agents.15_codereview",
}

for alias, real in agent_mappings.items():
    try:
        mod = importlib.import_module(real)
        sys.modules[alias] = mod
        
        try:
            agent_mod = importlib.import_module(f"{real}.agent")
            sys.modules[f"{alias}.agent"] = agent_mod
        except ImportError:
            pass
    except ImportError:
        pass
