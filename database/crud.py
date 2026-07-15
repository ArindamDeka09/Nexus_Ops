# database/crud.py
# ----------------------------------------------------------------------
# Save and read operations for the Nexus-Ops database layer.
# Called by deploy_node to archive completed pipeline runs.
# ----------------------------------------------------------------------

from typing import Optional, List
from sqlalchemy.orm import Session
from database.models import Incident, AgentTrace


def save_incident(db: Session, state: dict) -> Incident:
    """
    Creates a new Incident record from the final AgentState.

    Args:
        db:    SQLAlchemy session (from get_db())
        state: The completed AgentState dict from LangGraph

    Returns:
        The saved Incident ORM object with its generated ID.
    """
    incident = Incident(
        issue_description  = state.get("issue_description", ""),
        category           = state.get("category", "Unknown"),
        priority           = state.get("priority", 3),
        complexity         = state.get("complexity", "Unknown"),
        root_cause_analysis= state.get("root_cause_analysis", ""),
        draft_fix          = state.get("draft_fix", ""),
        audit_verdict      = state.get("audit_reasoning", "PENDING"),
        audit_reasoning    = state.get("audit_reasoning", ""),
        tests_passed       = state.get("test_results", {}).get("passed", False),
        test_details       = state.get("test_results", {}).get("details", ""),
        iteration_count    = state.get("iteration_count", 0),
        ragas_faithfulness = state.get("ragas_faithfulness", None),
        ragas_relevancy    = state.get("ragas_relevancy", None),
        final_report       = state.get("final_report", ""),
    )
    db.add(incident)
    db.commit()
    db.refresh(incident)
    print(f"[Database] Incident archived → ID: {incident.id}")
    return incident


def save_agent_trace(
    db:         Session,
    incident_id: int,
    agent_role:  str,
    stage:       str,
    output_text: str,
    iteration:   int = 1,
) -> AgentTrace:
    """Saves one agent's output for a given incident run."""
    trace = AgentTrace(
        incident_id = incident_id,
        agent_role  = agent_role,
        stage       = stage,
        output_text = output_text,
        iteration   = iteration,
    )
    db.add(trace)
    db.commit()
    db.refresh(trace)
    return trace


def get_all_incidents(db: Session, limit: int = 50) -> List[Incident]:
    """Returns the most recent incidents, newest first."""
    return (
        db.query(Incident)
        .order_by(Incident.created_at.desc())
        .limit(limit)
        .all()
    )


def get_incident_by_id(db: Session, incident_id: int) -> Optional[Incident]:
    """Returns a single incident with all its agent traces."""
    return db.query(Incident).filter(Incident.id == incident_id).first()


def get_pass_rate(db: Session) -> dict:
    """Returns overall pipeline pass/fail statistics."""
    total  = db.query(Incident).count()
    passed = db.query(Incident).filter(Incident.tests_passed == True).count()
    return {
        "total":     total,
        "passed":    passed,
        "failed":    total - passed,
        "pass_rate": round((passed / total * 100), 1) if total > 0 else 0.0,
    }