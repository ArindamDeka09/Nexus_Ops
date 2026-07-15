# agents/auditor.py
import os
from crewai import Agent
from agents.llm_config import build_swarm_llm

def create_auditor_agent() -> Agent:
    return Agent(
        role="Security & Quality Auditor",
        goal="Review the fix in under 200 words. End your response with exactly one of these two lines:\nVERDICT: APPROVED\nVERDICT: REJECTED - [one sentence reason]",
        backstory="You are a defensive security engineer. You approve only fixes that are correct and safe.",
        llm=build_swarm_llm(temperature=0.1),
        verbose=True,
        allow_delegation=False,
        max_iter=2
    )