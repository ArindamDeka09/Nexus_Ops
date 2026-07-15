# agents/crew.py  — clean version, no delays needed

from crewai import Crew, Task, Process
from agents.researcher import create_researcher_agent
from agents.coder      import create_coder_agent
from agents.auditor    import create_auditor_agent


def run_diagnosis_crew(
    issue_description: str,
    code_context:      str,
    root_cause_hint:   str,
) -> dict:

    researcher = create_researcher_agent()
    coder      = create_coder_agent()
    auditor    = create_auditor_agent()

    research_task = Task(
        description=(
            f"Analyse this bug report and code context.\n\n"
            f"BUG REPORT:\n{issue_description}\n\n"
            f"CODE CONTEXT:\n{code_context[:2000]}\n\n"
            f"HINT:\n{root_cause_hint[:500]}\n\n"
            f"Output exactly three sections: "
            f"AFFECTED COMPONENT, ROOT CAUSE, FIX STRATEGY."
        ),
        agent=researcher,
        expected_output="Three-section technical report: AFFECTED COMPONENT, ROOT CAUSE, FIX STRATEGY.",
    )

    coding_task = Task(
        description=(
            f"Using the Researcher's report, write the minimal Python fix.\n"
            f"Bug: {issue_description}\n"
            f"Rules: No new dependencies. Inline comments. Output code only."
        ),
        agent=coder,
        expected_output="A Python code block with inline comments. Nothing else.",
        context=[research_task],
    )

    audit_task = Task(
        description=(
            f"Review the fix for this bug: {issue_description}\n"
            f"Check: correctness, safety, readability.\n"
            f"Your final line must be exactly one of:\n"
            f"VERDICT: APPROVED\n"
            f"VERDICT: REJECTED - [one sentence reason]"
        ),
        agent=auditor,
        expected_output="Short review ending with VERDICT: APPROVED or VERDICT: REJECTED - [reason].",
        context=[research_task, coding_task],
    )

    crew = Crew(
        agents=[researcher, coder, auditor],
        tasks=[research_task, coding_task, audit_task],
        process=Process.sequential,
        verbose=True,
    )

    print("\n🤖 [Crew] Launching autonomous swarm (local Ollama)...")
    result = crew.kickoff()

    task_outputs    = result.tasks_output
    root_cause      = task_outputs[0].raw if len(task_outputs) > 0 else "Unavailable."
    draft_fix       = task_outputs[1].raw if len(task_outputs) > 1 else "Unavailable."
    audit_full      = task_outputs[2].raw if len(task_outputs) > 2 else "VERDICT: REJECTED - Audit failed."

    audit_approved  = "VERDICT: APPROVED" in audit_full
    audit_reasoning = audit_full.split("VERDICT:")[-1].strip()

    return {
        "root_cause":      root_cause,
        "draft_fix":       draft_fix,
        "audit_verdict":   "APPROVED" if audit_approved else "REJECTED",
        "audit_reasoning": audit_reasoning,
        "audit_approved":  audit_approved,
    }