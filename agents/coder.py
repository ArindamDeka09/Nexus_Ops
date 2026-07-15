# agents/coder.py
import os
from crewai import Agent
from agents.llm_config import build_swarm_llm

def create_coder_agent() -> Agent:
    return Agent(
        role="Principal Software Engineer",
        goal="Write a minimal Python fix based on the Researcher's diagnosis. Output the corrected code block with inline comments. No prose before or after the code.",
        backstory="You are a pragmatic engineer. The best fix is the smallest one that works.",
        llm=build_swarm_llm(temperature=0.1),
        verbose=True,
        allow_delegation=False,
        max_iter=2
    )