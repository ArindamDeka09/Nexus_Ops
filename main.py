# main.py
# ----------------------------------------------------------------------
# Nexus-Ops Main Entry Point: Compiles the full 6-stage LangGraph machine
# ----------------------------------------------------------------------

import os
from dotenv import load_dotenv
from orchestration.graph import build_graph

# Load environment elements (API Keys)
load_dotenv()

def run_pipeline(issue: str, codebase_path: str = "./", language: str = "Python"):
    """Runs a full incident through the Nexus-Ops agentic pipeline."""
    print("\n🚀 [System] Initializing Nexus-Ops Agentic Pipeline...")
    
    # Compile the LangGraph state machine from your graph module
    graph = build_graph()
    
    # Initialize the complete AgentState dictionary structure
    initial_state = {
        # Stage 1 Inputs
        "issue_description": issue,
        "category": "Unknown",
        "priority": 3,
        
        # Stage 2 Inputs
        "codebase_path": codebase_path,
        "language": language,
        "database_summary": None,
        "relevant_patterns": None,
        "sub_tasks": None,
        "complexity": None,
        "implementation_plan": None,
        "files_to_create": None,
        "files_to_modify": None,
        
        # Stages 3-6 (Populated dynamically by agents/nodes)
        "relevant_code_chunks": [],
        "root_cause_analysis": "",
        "draft_fix": "",
        "test_results": {},
        "iteration_count": 0,
        "audit_status": False,
        "guard_reasoning": None,
        "final_report": None
    }
    
    print(f"📥 [System] Incident received: '{issue}'")
    print("=" * 60)
    
    # Invoke the entire pipeline sequentially (including CrewAI swarm & pytest)
    final_state = graph.invoke(initial_state)
    
    print("=" * 60)
    print("\n✅ [System] Pipeline execution complete!")
    return final_state

if __name__ == "__main__":
    # Define our targeted anomaly case files
    target_issue = (
        "CRITICAL FAILURE: Payment processing module crashes with an unhandled "
        "TypeError when the checkout amount field is missing or passed as None."
    )
    target_repo = os.path.abspath(".")
    
    # Execute the master pipeline
    run_pipeline(issue=target_issue, codebase_path=target_repo, language="Python")