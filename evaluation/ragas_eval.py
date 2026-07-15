# evaluation/ragas_eval.py
# ----------------------------------------------------------------------
# Mathematical evaluation of agent outputs using Ragas.
# Uses Ollama llama3.2 as the LLM judge — no API calls, no rate limits.
#
# Metrics:
#   Faithfulness   — Is the fix derived from the retrieved code context?
#                    Prevents hallucination.
#   Answer Relevancy — Is the fix a direct, minimal solution?
#                    Prevents over-engineered responses.
# ----------------------------------------------------------------------

import os
from typing import Optional

from datasets import Dataset
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy
from ragas.llms import LangchainLLMWrapper
from ragas.embeddings import LangchainEmbeddingsWrapper
from langchain_ollama import ChatOllama
from langchain_ollama import OllamaEmbeddings


def build_ragas_evaluator():
    """
    Configures Ragas to use local Ollama models as judge and embedder.
    Returns configured metric objects ready for evaluation.
    """
    print("[Ragas] Configuring local Ollama judge...")

    # LLM judge: uses llama3.2 to score faithfulness and relevancy
    llm_judge = LangchainLLMWrapper(
        ChatOllama(model="llama3.2", temperature=0)
    )

    # Embedding model: converts text to vectors for similarity scoring
    embedder = LangchainEmbeddingsWrapper(
        OllamaEmbeddings(model="llama3.2")
    )

    # Configure each metric with the local models
    faithfulness.llm       = llm_judge
    answer_relevancy.llm   = llm_judge
    answer_relevancy.embeddings = embedder

    print("[Ragas] Judge and embedder configured.")
    return [faithfulness, answer_relevancy]


def evaluate_agent_output(
    issue_description:    str,
    root_cause_analysis:  str,
    draft_fix:            str,
    code_context_chunks:  list,
) -> dict:
    """
    Scores the agent's diagnosis and fix using Ragas metrics.

    Args:
        issue_description:   The original bug report (question).
        root_cause_analysis: The Researcher's analysis (part of answer).
        draft_fix:           The Coder's fix (part of answer).
        code_context_chunks: The RAG-retrieved code snippets (contexts).

    Returns:
        dict with faithfulness and answer_relevancy scores (0.0 to 1.0).
    """
    print("\n[Ragas] Running evaluation...")

    # Combine agent outputs into one answer string for scoring
    combined_answer = (
        f"ROOT CAUSE:\n{root_cause_analysis}\n\n"
        f"PROPOSED FIX:\n{draft_fix}"
    )

    # Ragas expects a HuggingFace Dataset format
    eval_dataset = Dataset.from_dict({
        "question":  [issue_description],
        "answer":    [combined_answer],
        "contexts":  [code_context_chunks if code_context_chunks else ["No context retrieved."]],
    })

    try:
        metrics = build_ragas_evaluator()
        results = evaluate(eval_dataset, metrics=metrics)

        scores = results.to_pandas()
        faith_score   = round(float(scores["faithfulness"].iloc[0]),    3)
        rel_score     = round(float(scores["answer_relevancy"].iloc[0]), 3)

        print(f"[Ragas] ✅ Faithfulness    : {faith_score}")
        print(f"[Ragas] ✅ Answer Relevancy: {rel_score}")

        return {
            "faithfulness":     str(faith_score),
            "answer_relevancy": str(rel_score),
            "status":           "evaluated",
        }

    except Exception as e:
        print(f"[Ragas] ⚠️  Evaluation skipped: {e}")
        return {
            "faithfulness":     "N/A",
            "answer_relevancy": "N/A",
            "status":           f"skipped: {str(e)[:80]}",
        }