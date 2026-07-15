# orchestration/graph.py
# ----------------------------------------------------------------------
# Central LangGraph Coordination Architecture Mapping Core.
# Wires up Stage 0 (Scanning Engine) and Stage 7 (Architectural Auditor)
# inside a functional graph builder with self-healing conditional routing.
# ----------------------------------------------------------------------

from langgraph.graph import StateGraph, END, START
from orchestration.state import AgentState
from orchestration.nodes import (
    scan_node,
    triage_node,
    research_node,
    diagnosis_node,
    testing_node,
    audit_node,
    deploy_node,
    feature_proposal_node,
    should_retry,
)

# ── DUAL ENTRY CONDITIONAL ROUTING FUNCTION ─────────────────────────
def route_entry_point(state: dict) -> str:
    """Dynamically determines if the system boots into standard triage or auto-scan."""
    if state.get("scan_mode") == "auto_scan":
        print("🔀 [Graph Router] Ingestion route selected: Autonomous Codebase Sweeping Pass.")
        return "scan"
    else:
        print("🔀 [Graph Router] Ingestion route selected: Targeted Manual Defect Triage.")
        return "triage"


def build_graph():
    # 1. Create a new graph with our AgentState as its memory
    graph = StateGraph(AgentState)

    # 2. Register every node (stage) with a name
    graph.add_node("scan",             scan_node)
    graph.add_node("triage",           triage_node)
    graph.add_node("research",         research_node)
    graph.add_node("diagnosis",        diagnosis_node)
    graph.add_node("testing",          testing_node)
    graph.add_node("audit",            audit_node)
    graph.add_node("deploy",           deploy_node)
    graph.add_node("feature_proposal", feature_proposal_node)

    # 3. Establish the master Entry Point conditional router logic gate
    graph.add_conditional_edges(
        START,
        route_entry_point,
        {
            "scan": "scan",
            "triage": "triage"
        }
    )

    # 4. Add straight-line edges (always go A → B)
    graph.add_edge("scan",     "triage")
    graph.add_edge("triage",    "research")
    graph.add_edge("research",  "diagnosis")
    graph.add_edge("diagnosis", "testing")

    # 5. Add a CONDITIONAL edge after testing (Self-Healing Control Loop)
    graph.add_conditional_edges(
        "testing",
        should_retry,
        {
            "audit":    "audit",
            "retry":    "diagnosis",
            "escalate": "deploy",  # Graceful exit to deploy if max retries hit
        }
    )

    # 6. Final execution loops mapping routes down to the end anchors
    graph.add_edge("audit", "deploy")
    graph.add_edge("deploy", "feature_proposal")
    graph.add_edge("feature_proposal", END)

    # 7. Compile and return
    compiled = graph.compile()
    print("✅ Nexus-Ops graph compiled successfully with Phase 5 expansions.")
    return compiled


# Make graph importable as a singleton matching your original framework hook
nexus_graph = build_graph()