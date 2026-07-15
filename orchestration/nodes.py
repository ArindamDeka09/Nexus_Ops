# orchestration/nodes.py (Phase 5 — INTEGRATED MASTER FILE)
# ----------------------------------------------------------------------

import os
import subprocess
import sys
from dotenv import load_dotenv

# Import the base configuration, state framework, and agent interfaces
from orchestration.state import AgentState
from cognition.rag_engine import CodeRAGEngine
from cognition.dspy_signatures import configure_dspy, DecomposeTask, PlanCode
from agents.crew import run_diagnosis_crew 

# Import safety utilities recommended by Claude's Phase 3 Bridge
from orchestration.patcher import patch_state, validate_required

load_dotenv()

_rag_engine: CodeRAGEngine = None
_dspy_configured = False


def _get_rag_engine(codebase_path: str) -> CodeRAGEngine:
    global _rag_engine
    if _rag_engine is None:
        print(f"[Nodes] Initializing CodeRAGEngine for: {codebase_path}")
        _rag_engine = CodeRAGEngine()
    return _rag_engine


def _ensure_dspy():
    global _dspy_configured
    if not _dspy_configured:
        configure_dspy()
        _dspy_configured = True


# ── Stage 1: Triage ───────────────────────────────────────────────────
def triage_node(state: dict) -> dict:
    print("\n[Stage 1] Triage Node running...")
    current_state = patch_state(state)
    print(f"   Incident: {current_state['issue_description']}")
    return {"category": "Bug", "priority": 2}


# ── Stage 2: Research ─────────────────────────────────────────────────
def research_node(state: dict) -> dict:
    print("\n[Stage 2] Research Node running...")
    current_state = patch_state(state)

    target_path = current_state.get("codebase_path") or "./"
    rag = _get_rag_engine(target_path)
    _ensure_dspy()

    summary  = rag.get_codebase_summary()
    patterns = rag.find_relevant_patterns(
        f"{current_state['issue_description']} in language context {current_state.get('language', 'Python')}"
    )

    decomposer    = DecomposeTask()
    decomposition = decomposer(
        task_description=current_state["issue_description"],
        codebase_context=summary
    )

    planner = PlanCode()
    plan    = planner(
        task_description=current_state["issue_description"],
        existing_patterns=patterns,
        language=current_state.get("language", "Python")
    )

    return {
        "codebase_summary":    summary,
        "relevant_patterns":   patterns,
        "sub_tasks":           decomposition.sub_tasks,
        "complexity":          decomposition.estimated_complexity,
        "implementation_plan": plan.implementation_plan,
        "files_to_create":     plan.files_to_create,
        "files_to_modify":     plan.files_to_modify,
        "relevant_code_chunks": [patterns[:300] + "..."],
    }


# ── Stage 3: Diagnosis — USES CREWAI SWARM ────────────────────────────
def diagnosis_node(state: dict) -> dict:
    print("\n[Stage 3] Diagnosis Node — launching CrewAI swarm...")
    current_state = patch_state(state)

    # Gather context from previous stages safely
    code_context     = "\n\n".join(current_state.get("relevant_code_chunks", []))
    root_cause_hint  = current_state.get("implementation_plan", "No prior analysis available.")

    # Run the full Researcher → Coder → Auditor crew
    crew_result = run_diagnosis_crew(
        issue_description=current_state["issue_description"],
        code_context=code_context,
        root_cause_hint=root_cause_hint,
    )

    print(f"\n  [Swarm] Audit Verdict: {crew_result['audit_verdict']}")

    return {
        "root_cause_analysis": crew_result["root_cause"],
        "draft_fix":           crew_result["draft_fix"],
        "audit_status":        crew_result["audit_approved"],   # Pre-fill from crew
        "audit_reasoning":     crew_result["audit_reasoning"],
    }


# ── Stage 4: Testing — ENVIRONMENT INJECTED SUBPROCESS RUNNER ──────────
def testing_node(state: dict) -> dict:
    print("\n[Stage 4] Testing Node - executing pytest via subprocess...")
    
    # Sanitize current state dictionary inputs safely via utility
    current_state = patch_state(state)
    
    # Establish absolute runtime root directory path
    project_root = os.path.abspath(".")
    
    # Read or clone current environment parameters
    custom_env = os.environ.copy()
    existing_pythonpath = custom_env.get("PYTHONPATH", "")
    
    # Inject project root directly so pytest hooks can map modules flawlessly
    if existing_pythonpath:
        custom_env["PYTHONPATH"] = f"{project_root}{os.pathsep}{existing_pythonpath}"
    else:
        custom_env["PYTHONPATH"] = project_root
        
    print(f"🔹 [Testing] Project root injected into PYTHONPATH: {project_root}")
    
    # Run pytest cleanly inside a native subprocess block
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "tests/", "-v", "--tb=short"],
            capture_output=True,
            text=True,
            cwd=project_root,
            env=custom_env
        )
        
        # Analyze outcome signals
        return_code = result.returncode
        passed = (return_code == 0)
        stdout = result.stdout
        details = stdout[-2000:] if len(stdout) > 2000 else stdout
        if not passed and result.stderr:
            details += f"\n{result.stderr}"
        
    except Exception as e:
        return_code = -1
        passed = False
        details = f"Subprocess invocation crashed: {str(e)}"
        
    print(f"🔸 [Testing] Return code: {return_code}")
    if passed:
        print("✅ [Testing] All tests passed! Passing state to Security Audit.")
    else:
        print("❌ [Testing] Test suite failures caught. Triggering self-healing retry loop.")
        
    # Increment our historical loop count tracking metrics
    current_iteration = current_state.get("iteration_count", 0)
    
    # Package back cleanly to update the master state machine
    return {
        "test_results": {
            "passed": passed,
            "details": details,
            "returncode": return_code
        },
        "iteration_count": current_iteration + 1
    }


# ── Stage 5: Audit ────────────────────────────────────────────────────
def audit_node(state: dict) -> dict:
    print("\n[Stage 5] Audit Node running...")
    current_state = patch_state(state)

    # The Auditor already ran inside the CrewAI swarm in Stage 3.
    # This node reads that pre-filled result and applies the gate.
    audit_approved  = current_state.get("audit_status", False)
    audit_reasoning = current_state.get("audit_reasoning", "No audit reasoning available.")

    print(f"  [Audit] Verdict: {'✅ APPROVED' if audit_approved else '❌ REJECTED'}")
    print(f"  [Audit] Reasoning: {audit_reasoning[:150]}...")

    return {"audit_status": audit_approved}


# ── Stage 6: Deploy (updated report format) ───────────────────────────
def deploy_node(state: AgentState) -> dict:
    """
    Stage 6: Archives the completed incident to SQLite and runs Ragas scoring.
    """
    print("\n[Stage 6] Deploy Node running...")

    from orchestration.patcher import patch_state
    state = patch_state(state)

    # ── Run Ragas evaluation ──────────────────────────────────────────
    ragas_scores = {"faithfulness": "N/A", "answer_relevancy": "N/A"}
    try:
        from evaluation.ragas_eval import evaluate_agent_output
        ragas_scores = evaluate_agent_output(
            issue_description   = state["issue_description"],
            root_cause_analysis = state.get("root_cause_analysis", ""),
            draft_fix           = state.get("draft_fix", ""),
            code_context_chunks = state.get("relevant_code_chunks", []),
        )
        print(f"[Deploy] Ragas scores: {ragas_scores}")
    except Exception as e:
        print(f"[Deploy] Ragas evaluation skipped: {e}")

    # ── Compose final report ──────────────────────────────────────────
    report = (
        f"{'='*60}\n"
        f"        NEXUS-OPS AUTOMATED ANOMALY FINAL REPORT\n"
        f"{'='*60}\n"
        f"INCIDENT     : {state['issue_description']}\n"
        f"CATEGORY     : {state.get('category', 'N/A')} | "
        f"PRIORITY: {state.get('priority', 'N/A')}\n"
        f"COMPLEXITY   : {state.get('complexity', 'N/A')}\n\n"
        f"[ROOT CAUSE ANALYSIS]\n{state.get('root_cause_analysis', 'N/A')}\n\n"
        f"[DRAFT FIX]\n{state.get('draft_fix', 'N/A')}\n\n"
        f"[TEST RESULTS]\n{state['test_results'].get('details', 'N/A')}\n\n"
        f"[AUDIT VERDICT]\n{state.get('audit_reasoning', 'N/A')}\n\n"
        f"[RAGAS SCORES]\n"
        f"  Faithfulness    : {ragas_scores.get('faithfulness', 'N/A')}\n"
        f"  Answer Relevancy: {ragas_scores.get('answer_relevancy', 'N/A')}\n"
        f"{'='*60}"
    )
    print(f"\n{report}")

    # ── Archive to SQLite ─────────────────────────────────────────────
    updated_state = dict(state)
    updated_state["ragas_faithfulness"] = ragas_scores.get("faithfulness", "N/A")
    updated_state["ragas_relevancy"]    = ragas_scores.get("answer_relevancy", "N/A")
    updated_state["final_report"]       = report

    # Default fallback placeholder ID
    committed_incident_id = None

    try:
        from database.connection import SessionLocal, init_db
        from database.crud import save_incident
        init_db()
        db = SessionLocal()
        
        # Save overarching incident run record details to disk and catch return object
        db_incident = save_incident(db, updated_state)
        committed_incident_id = db_incident.id
        
        db.close()
        print(f"[Deploy] ✅ Incident archived to nexus_ops.db with Row ID: {committed_incident_id}")
    except Exception as e:
        print(f"[Deploy] ⚠️  Database archiving skipped: {e}")

    return {
        "final_report":       report,
        "ragas_faithfulness": ragas_scores.get("faithfulness", "N/A"),
        "ragas_relevancy":    ragas_scores.get("answer_relevancy", "N/A"),
        "last_incident_id":   committed_incident_id,
    }


# ── Router ────────────────────────────────────────────────────────────
def should_retry(state: dict) -> str:
    current_state = patch_state(state)
    tests_passed = current_state["test_results"].get("passed", False)
    retries      = current_state.get("iteration_count", 0)
    
    if tests_passed:
        print("\n  ✅ Tests passed — proceeding to audit.")
        return "audit"
    elif retries < 3:
        print(f"\n  🔁 Retry {retries}/3.")
        return "retry"
    else:
        print("\n  🚨 Max retries — escalating to human.")
        return "escalate"
    

# ======================================================================
# PHASE 5 EXTENSION NODES: AUTONOMOUS SCANNING & ARCHITECTURAL AUDITING
# ======================================================================

def scan_node(state: dict) -> dict:
    """
    Stage 0: Pre-processing step. Automatically crawls the repository target path,
    detects anomalies via AST static parsing, and pipes the top problem area
    directly into the self-healing triage engine queue.
    """
    print("\n🔍 [Stage 0] Scan Node running autonomous repository audit...")
    
    # Extract structural search configurations from state
    target_path = state.get("scan_path") or "./"
    
    from ingestion.scanner import scan_repository, issues_to_bug_report
    
    # Execute offline static syntax tree analysis sweep
    found_issues = scan_repository(target_path)
    
    # Translate structural anomalies array into standard textual report string
    auto_report = issues_to_bug_report(found_issues)
    
    # Isolate top critical item description payload to feed into Stage 1 Triage
    top_issue_desc = state.get("issue_description") or ""
    if found_issues and not top_issue_desc:
        top_issue_desc = (
            f"CRITICAL SYSTEM DEFECT: Automated AST scanner identified a high-risk "
            f"'{found_issues[0]['issue_type']}' inside module '{found_issues[0]['file_path']}' "
            f"(Line {found_issues[0]['line_number']}). Description: {found_issues[0]['description']}"
        )
    
    print(f"[Scan Node] Crawled workspace. Found {len(found_issues)} structural anomalies.")
    if found_issues:
        print(f"[Scan Node] Top critical finding piped into execution queue.")

    return {
        "issue_description": top_issue_desc,
        "detected_issues": found_issues,
        "scanned_files": len(set(iss["file_path"] for iss in found_issues)),
        "scan_mode": "auto_scan"
    }


def feature_proposal_node(state: dict) -> dict:
    """
    Stage 7: Post-processing step. Invokes the Principal Architect Agent
    to construct modular enhancement blueprints and records them to SQLite.
    """
    print("\n🏗️ [Stage 7] Feature Proposal Node analyzing architectural ecosystem...")
    
    # Safety boundary: only generate expansions when running in explicit Auto-Scan mode
    if state.get("scan_mode") != "auto_scan":
        print("[Feature Proposal Node] Bypassed. Pipeline executed via manual report channel.")
        return {"feature_proposals": []}
        
    codebase_profile = state.get("codebase_summary") or "Standard application structure."
    anomalies_list = state.get("detected_issues") or []
    parent_incident_id = state.get("last_incident_id")
    
    # Invoke the CrewAI Local Architect cluster pass
    from agents.feature_auditor import run_feature_audit
    generated_proposals = run_feature_audit(codebase_profile, anomalies_list)
    
    # Commit suggestions to SQLite database infrastructure
    if parent_incident_id and generated_proposals:
        try:
            from database.connection import SessionLocal
            from database.models import FeatureProposal
            
            db_session = SessionLocal()
            try:
                for prop in generated_proposals:
                    db_proposal = FeatureProposal(
                        incident_id=parent_incident_id,
                        title=prop.get("title", "System Upgrade"),
                        target_file=prop.get("target_file", "Global Core"),
                        effort=prop.get("effort", "Medium"),
                        description=prop.get("description", ""),
                        status="pending"
                    )
                    db_session.add(db_proposal)
                db_session.commit()
                print(f"[Feature Proposal Node] {len(generated_proposals)} feature proposals archived to DB successfully!")
            finally:
                db_session.close()
        except Exception as db_err:
            print(f"⚠️ [Feature Proposal Node] Database logging skipped: {str(db_err)}")
            
    return {"feature_proposals": generated_proposals}