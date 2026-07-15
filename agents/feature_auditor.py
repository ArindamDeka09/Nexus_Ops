# agents/feature_auditor.py
# ----------------------------------------------------------------------
# Feature Auditor Agent: Analyses the full codebase structure and
# proposes high-level architectural enhancements.
# Runs AFTER the bug-fix pipeline as a separate analysis pass.
# Updated with an ultra-robust line-by-line state-machine parser.
# ----------------------------------------------------------------------

import os
from crewai import Agent, Task, Crew, Process
from agents.llm_config import build_swarm_llm


def create_feature_auditor_agent() -> Agent:
    return Agent(
        role="Principal Architect & Feature Auditor",
        goal=(
            "Analyse the full codebase structure and propose 3-5 concrete, "
            "high-value architectural enhancements. Focus on: missing middleware, "
            "unvalidated input layers, absent caching, missing auth guards, "
            "insufficient logging, and scalability gaps. "
            "Be specific — reference actual file names and function signatures."
        ),
        backstory=(
            "You are a senior software architect with 15 years of experience "
            "scaling systems from prototype to production. You read codebases "
            "like blueprints and immediately see what's missing. "
            "You do not suggest vague improvements — every proposal includes "
            "a specific file, a specific function, and a specific fix pattern."
        ),
        llm=build_swarm_llm(temperature=0.3),
        verbose=True,
        allow_delegation=False,
        max_iter=2,
    )


def run_feature_audit(codebase_summary: str, detected_issues: list) -> list:
    """
    Runs the Feature Auditor agent on the codebase summary and returns
    a list of structured feature proposals.

    Returns:
        List of dicts, each with: title, description, target_file,
        effort (Low/Medium/High), status ("pending")
    """
    print("\n[Feature Auditor] Running architectural audit...")

    issue_summary = "\n".join([
        f"- [{i['severity']}] {i['file_path']}: {i['description'][:100]}"
        for i in (detected_issues or [])[:5]
    ])

    auditor = create_feature_auditor_agent()

    audit_task = Task(
        description=(
            f"Analyse this codebase and propose architectural enhancements.\n\n"
            f"CODEBASE SUMMARY:\n{codebase_summary[:3000]}\n\n"
            f"KNOWN ISSUES ALREADY BEING FIXED:\n{issue_summary}\n\n"
            f"Your proposals must NOT overlap with the known issues above.\n"
            f"Focus on structural gaps: missing layers, security blind spots, "
            f"performance bottlenecks, and scalability concerns.\n\n"
            f"Format your response as a numbered list. Each item must follow "
            f"this EXACT structure:\n"
            f"PROPOSAL: [Short title]\n"
            f"FILE: [target file path]\n"
            f"EFFORT: [Low / Medium / High]\n"
            f"DETAIL: [2-3 sentence description of the enhancement and why it matters]\n"
            f"---"
        ),
        agent=auditor,
        expected_output=(
            "3-5 architectural proposals, each with PROPOSAL, FILE, EFFORT, "
            "and DETAIL fields, separated by ---"
        ),
    )

    crew   = Crew(agents=[auditor], tasks=[audit_task], process=Process.sequential)
    result = crew.kickoff()
    raw    = result.tasks_output[0].raw if result.tasks_output else ""

    # Parse proposals using the ultra-robust state-machine parser
    proposals = _parse_proposals_text(raw)
    print(f"[Feature Auditor] Generated {len(proposals)} proposal(s).")
    return proposals


def _parse_proposals_text(raw_text: str) -> list:
    """
    Ultra-robust state-machine parser for Feature Auditor agent output.
    Handles 'Final Answer:' prefixes, '---' separators, mixed casing,
    extra whitespace, inline formatting, and multi-line DETAIL fields.
    Uses fuzzy line-by-line matching.
    """
    # ── Step 1: Strip known LLM preamble prefixes ────────────────────
    lines = raw_text.splitlines()
    cleaned_lines = []
    for line in lines:
        stripped = line.strip()
        # Skip pure preamble lines
        if stripped.lower().startswith("final answer"):
            continue
        if stripped.lower().startswith("here are"):
            continue
        if stripped.lower().startswith("based on"):
            continue
        cleaned_lines.append(line)

    # ── Step 2: State-machine line parser ────────────────────────────
    proposals = []
    current = None        # The proposal dict being built
    current_field = None  # Which field we're currently appending to

    FIELD_KEYS = {
        "PROPOSAL": "title",
        "FILE":     "target_file",
        "EFFORT":   "effort",
        "DETAIL":   "description"
    }

    def save_current():
        """Saves current proposal if it has at least a title and description."""
        nonlocal current
        if current and current.get("title") and current.get("description"):
            proposals.append({
                "title":       current.get("title", "").strip(),
                "target_file": current.get("target_file", "main.py").strip(),
                "effort":      current.get("effort", "Medium").strip(),
                "description": current.get("description", "").strip(),
                "status":      "pending"
            })

    for line in cleaned_lines:
        stripped = line.strip()

        # Skip pure separator lines
        if not stripped or set(stripped) <= {'-', '=', '*', '#', ' '}:
            continue

        # Detect which field this line starts
        matched_key = None
        matched_value = None

        line_upper = stripped.upper()

        for keyword, field_name in FIELD_KEYS.items():
            kw_upper = keyword.upper()

            # Check if line contains the keyword
            idx = line_upper.find(kw_upper)
            if idx == -1:
                continue

            # Make sure it's followed by a colon somewhere after it
            colon_idx = stripped.find(":", idx)
            if colon_idx == -1:
                continue

            # Extract everything after the first colon for the value
            value_after_colon = stripped[colon_idx + 1:].strip()
            matched_key = field_name
            matched_value = value_after_colon
            break

        if matched_key == "title":
            # Starting a new proposal -> save the previous one first
            save_current()
            current = {"title": matched_value}
            current_field = "title"

        elif matched_key and current is not None:
            # Adding a field to the current proposal
            current[matched_key] = matched_value
            current_field = matched_key

        elif current is not None and current_field == "description":
            # Multi-line DETAIL continuation -> append to description
            existing = current.get("description", "")
            current["description"] = (existing + " " + stripped).strip()

    # Save the final proposal after the loop ends
    save_current()

    # ── Step 3: Deduplicate by title ──────────────────────────────────
    seen_titles = set()
    unique = []
    for p in proposals:
        if p["title"] not in seen_titles:
            seen_titles.add(p["title"])
            unique.append(p)

    result = unique[:5]  # Cap at 5
    print(f"[Feature Auditor] Parsed {len(result)} proposal(s) from agent output.")
    return result