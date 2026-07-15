# orchestration/patcher.py
# ----------------------------------------------------------------------
# State validation and sanitization utility to safeguard AgentState data.
# ----------------------------------------------------------------------

from typing import Any

# Global defaults mapper to safely populate empty or missing fields
STATE_DEFAULTS: dict[str, Any] = {
    "issue_description": "No issue provided.",
    "category": "Unknown",
    "priority": 3,
    "codebase_path": "./",
    "language": "Python",
    "database_summary": None,
    "relevant_patterns": None,
    "sub_tasks": None,
    "complexity": None,
    "implementation_plan": None,
    "files_to_create": None,
    "files_to_modify": None,
    "relevant_code_chunks": [],
    "root_cause_analysis": "",
    "draft_fix": "",
    "test_results": {},
    "iteration_count": 0,
    "audit_status": False,
    "guard_reasoning": None,
    "final_report": None
}

def patch_state(state: dict) -> dict:
    """Fills any missing keys in the state dictionary with safe default values."""
    patched = state.copy()
    for key, default_value in STATE_DEFAULTS.items():
        if key not in patched or patched[key] is None:
            patched[key] = default_value
    return patched

def validate_required(state: dict, required_keys: list[str], node_name: str):
    """Raises a clear error if a critical key is missing before a dependent node runs."""
    for key in required_keys:
        if key not in state or not state[key]:
            raise RuntimeError(
                f"❌ [State Error] Validation failed at '{node_name}': "
                f"Missing critical required key '{key}'!"
            )