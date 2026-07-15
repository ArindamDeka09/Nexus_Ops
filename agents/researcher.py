# agents/researcher.py
import os
from crewai import Agent
from agents.llm_config import build_swarm_llm

def create_researcher_agent() -> Agent:
    return Agent(
        role="Senior Code Researcher",
        goal="Analyse retrieved code snippets and the bug report. Identify exactly which function contains the defect and why. Be concise – limit your response to 300 words maximum.",
        backstory="You are a precise software archaeologist. You trace, verify, and report facts only.",
        llm=build_swarm_llm(temperature=0.2),
        verbose=True,
        allow_delegation=False,
        max_iter=2
    )