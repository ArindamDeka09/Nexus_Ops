# orchestration/state.py
# ----------------------------------------------------------------------
# Centralized State Management for the Nexus-Ops Agentic Loop.
# Updated for Phase 5 to support dual execution paths: Targeted 
# Manual Reports and Autonomous Repository Sweeps.
# ----------------------------------------------------------------------

from typing import TypedDict, List, Dict, Optional, Any


class AgentState(TypedDict):
    # Stage 1: Triage
    issue_description:   str
    category:            str
    priority:            int

    # Stage 2: Research — Existing architecture configuration properties
    codebase_path:       Optional[str]
    language:            Optional[str]
    codebase_summary:    Optional[str]
    relevant_patterns:   Optional[str]
    sub_tasks:           Optional[str]
    complexity:          Optional[str]
    implementation_plan: Optional[str]
    files_to_create:     Optional[str]
    files_to_modify:     Optional[str]

    # Existing fields
    relevant_code_chunks: List[str]

    # Stage 3: Diagnosis
    root_cause_analysis: str
    draft_fix:           str

    # Stage 4: Testing
    test_results:        Dict
    iteration_count:     int

    # Stage 5: Audit
    audit_status:        bool
    audit_reasoning:     Optional[str]

    # Stage 6: Deploy
    final_report:        Optional[str]

    # ── PHASE 5 SCANNING & AUDITING STATE EXTENSIONS ──────────────────
    scan_mode:           Optional[str]   # "manual" or "auto_scan"
    scan_path:           Optional[str]   # Root directory target string path
    detected_issues:     List[Dict[str, Any]] # Collection of problems from AST scanner
    scanned_files:       Optional[int]   # Cumulative count of files searched
    feature_proposals:   List[Dict[str, Any]] # Structural recommendations list
    last_incident_id:    Optional[int]   # Tracking key mapping parent relational row
    ragas_faithfulness:  Optional[str]   # Math matrix metrics evaluation string
    ragas_relevancy:     Optional[str]   # Quality metric scoring verification string