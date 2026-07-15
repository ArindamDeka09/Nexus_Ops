#!/usr/bin/env python3
# demo_vector_search.py
# -------------------------------------------------------
# Standalone demo: LlamaIndex Semantic Vector Search
# Run with: python demo_vector_search.py
# -------------------------------------------------------

import os
import sys

# ── Runtime patch: bypass broken numpy version detection ─────────────
# The numpy installation in this venv is missing its RECORD file,
# so importlib.metadata.version("numpy") returns None, which causes
# transformers' version checker to crash with "found=None".
# This patch intercepts the metadata lookup for numpy only and
# returns a safe fallback version string before anything else imports.
try:
    import importlib.metadata as _meta
    _original_version = _meta.version

    def _safe_version(package_name: str) -> str:
        if package_name.lower() in ("numpy", "numpy_"):
            return "1.26.4"          # satisfies all >=1.17 checks
        return _original_version(package_name)

    _meta.version = _safe_version
except Exception:
    pass   # if patching fails, continue anyway

# ── Also suppress any advisory warnings from transformers ─────────────
os.environ["TRANSFORMERS_NO_ADVISORY_WARNINGS"] = "1"
os.environ["TOKENIZERS_PARALLELISM"] = "false"   # silences a noisy fork warning

# ── Colour helpers ────────────────────────────────────────────────────
CYAN   = "\033[96m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
BOLD   = "\033[1m"
RESET  = "\033[0m"

def header(text):
    print(f"\n{BOLD}{CYAN}{'─'*60}{RESET}")
    print(f"{BOLD}{CYAN}  {text}{RESET}")
    print(f"{BOLD}{CYAN}{'─'*60}{RESET}")

def step(n, text):
    print(f"\n{YELLOW}[Step {n}]{RESET} {text}")

def success(text):
    print(f"{GREEN}  ✅ {text}{RESET}")


# ── Main demo ─────────────────────────────────────────────────────────
def run_demo():
    print(f"\n{BOLD}{'='*60}{RESET}")
    print(f"{BOLD}  NEXUS-OPS │ Live Semantic Vector Search Demo{RESET}")
    print(f"{BOLD}  Powered by LlamaIndex + HuggingFace Embeddings{RESET}")
    print(f"{BOLD}{'='*60}{RESET}")

    # ── Step 1: Load embedding model ──────────────────────────────────
    step(1, "Loading local HuggingFace embedding model...")
    print(f"       Model: sentence-transformers/all-MiniLM-L6-v2")
    print(f"       Runs entirely on-device — zero API calls required.\n")

    from llama_index.core import Settings
    from llama_index.embeddings.huggingface import HuggingFaceEmbedding

    embed_model = HuggingFaceEmbedding(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    Settings.embed_model = embed_model
    Settings.llm = None
    success("Embedding model loaded.")

    # ── Step 2: Load source code ──────────────────────────────────────
    step(2, "Loading payment module source code from disk...")
    from llama_index.core import SimpleDirectoryReader

    reader = SimpleDirectoryReader(
        input_dir="./payment",
        required_exts=[".py"],
        recursive=True,
        filename_as_id=True,
    )
    documents = reader.load_data()
    success(f"Loaded {len(documents)} file(s) from payment/")
    for doc in documents:
        print(f"       📄 {doc.metadata.get('file_name', 'unknown')}")

    # ── Step 3: Split into semantic chunks ────────────────────────────
    step(3, "Splitting code into semantic chunks using SentenceSplitter...")
    print(f"       Strategy: Token-aware splitting with sentence boundary detection")
    print(f"       Chunk size: 400 tokens | Overlap: 50 tokens\n")

    from llama_index.core.node_parser import SentenceSplitter
    splitter = SentenceSplitter(
        chunk_size=400,
        chunk_overlap=50,
    )
    nodes = splitter.get_nodes_from_documents(documents)
    success(f"Created {len(nodes)} semantic code chunk(s).")
    print(f"\n       Sample chunks:")
    for i, node in enumerate(nodes[:3]):
        preview = node.text[:80].replace("\n", " ").strip()
        print(f"       Chunk {i+1}: {preview}...")

    # ── Step 4: Build vector index ────────────────────────────────────
    step(4, "Embedding chunks and building in-memory VectorStoreIndex...")
    print(f"       Each chunk → 384-dimensional embedding vector.")
    print(f"       Similarity search uses cosine distance.\n")

    import time
    t0 = time.time()

    from llama_index.core import VectorStoreIndex
    index = VectorStoreIndex(nodes, show_progress=True)

    elapsed = round(time.time() - t0, 2)
    success(f"Vector index built in {elapsed}s — {len(nodes)} chunks embedded.")

    # ── Step 5: Semantic similarity search ───────────────────────────
    header("LIVE SEMANTIC SEARCH RESULTS")
    print("  Demonstrating concept-level retrieval — no keyword matching:\n")

    from llama_index.core.retrievers import VectorIndexRetriever

    queries = [
        (
            "null check before payment processing",
            "Should find the None guard — even if the word 'null' is not in the code"
        ),
        (
            "currency validation logic",
            "Should find currency enforcement — no word 'validate' needed"
        ),
        (
            "transaction fee calculation",
            "Should find the fee arithmetic — no word 'fee' needed in the function"
        ),
    ]

    retriever = VectorIndexRetriever(index=index, similarity_top_k=2)

    for query, explanation in queries:
        print(f"  {BOLD}Query:{RESET}  \"{query}\"")
        print(f"  {YELLOW}Point:{RESET}  {explanation}")
        print(f"  {'─'*54}")

        results = retriever.retrieve(query)
        for i, result in enumerate(results):
            score   = round(result.score, 4) if result.score else 0.0
            source  = result.metadata.get("file_name", "unknown")
            snippet = result.text[:120].replace("\n", " ").strip()
            bar_len = int(score * 20)
            bar     = "█" * bar_len + "░" * (20 - bar_len)

            print(f"\n  {GREEN}  Result {i+1}:{RESET}")
            print(f"    Source : {source}")
            print(f"    Score  : {score}  [{bar}]")
            print(f"    Code   : {snippet}...")

        print()

    # ── Step 6: Key contrast ─────────────────────────────────────────
    header("KEYWORD SEARCH vs SEMANTIC SEARCH")
    print(f"""
  Keyword / grep approach:
    Searches for exact string tokens.
    "null check"  →  only matches lines containing "null" and "check".
    Misses: None guards, 'if not amount', 'if amount is None', etc.

  Semantic vector search (this pipeline):
    Converts intent to a point in 384-dimensional space.
    "null check"  →  finds code that IS a null check, regardless
    of which words were used to write it.

  This is the production upgrade path for Nexus-Ops:
  replace CodeRAGEngine's full-context dump with targeted
  semantic retrieval — reducing prompt size and improving
  agent accuracy on large, enterprise-scale codebases.
""")

    print(f"{BOLD}{'='*60}{RESET}")
    print(f"{BOLD}  Demo complete. Semantic pipeline fully operational.{RESET}")
    print(f"{BOLD}{'='*60}{RESET}\n")


if __name__ == "__main__":
    if sys.platform == "win32":
        os.system("color")   # enable ANSI colours on Windows
    run_demo()