# agents/llm_config.py
# -------------------------------------------------------
# Local Ollama LLM — zero API calls, zero rate limits.
# Aligns with the original hybrid model architecture:
# Ollama handles local agent reasoning,
# Gemini handles the high-level DSPy planning (Stage 2).
# -------------------------------------------------------

from crewai import LLM


def build_swarm_llm(temperature: float = 0.2) -> LLM:
    """
    Returns a local Ollama LLM instance for CrewAI agents.
    Requires Ollama running at localhost:11434.
    """
    return LLM(
        model="ollama/llama3.2",
        base_url="http://localhost:11434",
        temperature=temperature,
    )