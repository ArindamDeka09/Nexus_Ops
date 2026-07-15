# 🤖 Nexus Ops
### Autonomous Codebase Self-Healing Platform

> 🎓 **This project was developed as a Final Year Project for the Bachelor of Computer Applications (BCA) degree — Semester VI.**
> **Candidate:** Arindam Deka | **Domain:** AIOps — Artificial Intelligence for IT Operations

[![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python)](https://python.org)
[![LangGraph](https://img.shields.io/badge/LangGraph-Orchestration-orange)](https://github.com/langchain-ai/langgraph)
[![CrewAI](https://img.shields.io/badge/CrewAI-Multi--Agent-red)](https://crewai.com)
[![Ollama](https://img.shields.io/badge/Ollama-Local%20LLM-green)](https://ollama.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-ff4b4b?logo=streamlit)](https://streamlit.io)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

---

## 📌 About This Project

**Nexus Ops** is a fully autonomous, multi-agent AI platform built to act as a *Junior Site Reliability Engineer (SRE)*. It scans Python codebases for bugs and vulnerabilities, autonomously diagnoses the root cause using a swarm of specialised AI agents, generates a minimal code patch, validates it through an automated test suite, and archives the entire incident trace — all without human intervention at each step.

The system introduces an **Agentic Software Development Lifecycle (Agentic SDLC)** paradigm where the traditional human-in-the-loop maintenance workflow is replaced by a closed-loop, stateful agent graph that self-corrects and escalates intelligently.

> **Problem Solved:** In modern engineering environments, between 60–80% of developer bandwidth is consumed by maintenance, debugging, and triage. Nexus Ops eliminates this bottleneck by automating the full investigation → repair → verification → archiving loop.

---

## 🏗️ System Architecture

Nexus Ops is built on a **Tri-Layer Agentic Architecture**:

```text
┌─────────────────────────────────────────────────────────────┐
│                LAYER 1: INGESTION & PERCEPTION              │
│   RepositoryScanner (AST) │ CodeRAGEngine │ LlamaIndex      │
├─────────────────────────────────────────────────────────────┤
│                LAYER 2: COGNITIVE REASONING                 │
│   DSPy (DecomposeTask, PlanCode) │ Google Gemini API        │
├─────────────────────────────────────────────────────────────┤
│            LAYER 3: ORCHESTRATION & PERSISTENCE             │
│   LangGraph StateGraph │ CrewAI Swarm │ SQLite + SQLAlchemy │
└─────────────────────────────────────────────────────────────┘

```

### 🔄 6-Stage Autonomous Pipeline

[Stage 0] Repository Scan  ──►  AST static analysis across all .py files
[Stage 1] Triage           ──►  Classify defect category and priority
[Stage 2] Research         ──►  RAG context extraction + DSPy planning
[Stage 3] Diagnosis        ──►  CrewAI 3-agent swarm generates patch
[Stage 4] Testing          ──►  Pytest subprocess validation
└──► Self-Healing Loop ──►  Retry up to 3x on failure (via SelfHealingRouter)
[Stage 5] Audit            ──►  Security & quality gate (APPROVED / REJECTED)
[Stage 6] Deploy           ──►  Archive to SQLite + Ragas evaluation scores
[Stage 7] Feature Audit    ──►  AI architectural enhancement proposals


## ✨ Key Features

| Feature | Description |
|---|---|
| 🔍 **AST Static Scanner** | Detects 6 defect classes: bare excepts, missing null checks, hardcoded secrets, unused imports, mutable defaults, missing type hints |
| 🤖 **CrewAI Multi-Agent Swarm** | Three specialised agents — Researcher, Coder, Auditor — collaborate sequentially to produce and review a repair patch |
| 🔁 **Self-Healing Retry Loop** | Automatically retries failed patches up to 3 times via `SelfHealingRouter` before escalating to human review |
| 📊 **Ragas Evaluation** | Mathematically scores every fix on Faithfulness (0–1) and Answer Relevancy (0–1) using a local Ollama judge |
| 🧠 **Semantic Vector Search** | LlamaIndex + `all-MiniLM-L6-v2` sentence transformer enables concept-level codebase retrieval (no keyword matching) |
| 💡 **Feature Proposals** | Principal Architect agent generates up to 5 colour-coded architectural enhancement proposals after every scan |
| 🗄️ **Persistent Telemetry** | Every incident, agent trace, and proposal archived to SQLite via SQLAlchemy ORM |
| 🖥️ **Streamlit Dashboard** | Real-time pipeline telemetry with Bug Resolutions, Feature Proposals, Ragas Scores, Full Report, and Semantic Search tabs |
| 🔒 **Privacy-First Hybrid Model** | Sensitive logs processed locally via Ollama; only high-level planning routed to cloud (Gemini API) |



## 🛠️ Tech Stack

### Agentic Frameworks
| Library | Role |
|---|---|
| [LangGraph](https://github.com/langchain-ai/langgraph) | Stateful 6-stage pipeline orchestration via `StateGraph` |
| [CrewAI](https://crewai.com) | Role-based 3-agent swarm coordination |
| [DSPy](https://github.com/stanfordnlp/dspy) | Declarative prompt optimisation (replaces brittle prompt strings) |
| [LlamaIndex](https://llamaindex.ai) | Document ingestion, chunking, and vector retrieval |

### Language Models
| Model | Where Used |
|---|---|
| `Ollama llama3.2` (local, 3B) | All CrewAI agents + Ragas judge — zero API cost, full privacy |
| `Google Gemini API` | DSPy planning in Stage 2 (high-level task decomposition) |
| `all-MiniLM-L6-v2` (HuggingFace) | 384-dim code embeddings for semantic search |

### Backend & Storage
| Component | Role |
|---|---|
| Python 3.12 | Core language |
| SQLite + SQLAlchemy 2.0 | Incident telemetry persistence |
| pytest | Automated patch validation in subprocess |
| python-dotenv | Secure API key management |

### Evaluation & UI
| Component | Role |
|---|---|
| Ragas | LLM-as-a-Judge quality scoring |
| Streamlit | Interactive dashboard at `localhost:8501` |
| sentence-transformers | Embedding model runtime |

---

## 📁 Project Structure

```

Nexus_Ops/
│
├── agents/                    # CrewAI agent definitions
│   ├── researcher.py          # Senior Code Researcher agent
│   ├── coder.py               # Principal Software Engineer agent
│   ├── auditor.py             # Security & Quality Auditor agent
│   ├── crew.py                # RepairSwarm orchestrator
│   ├── feature_auditor.py     # Principal Architect agent
│   └── llm_config.py          # Shared Ollama LLM configuration
│
├── cognition/                 # Reasoning layer
│   ├── rag_engine.py          # CodeRAGEngine (filesystem context reader)
│   └── dspy_signatures.py     # DSPy DecomposeTask + PlanCode signatures
│
├── orchestration/             # LangGraph pipeline
│   ├── graph.py               # StateGraph assembly + compilation
│   ├── nodes.py               # All 6 pipeline stage node functions
│   ├── state.py               # AgentState TypedDict definition
│   └── patcher.py             # State validation + safe defaults
│
├── ingestion/                 # Data ingestion layer
│   ├── scanner.py             # RepositoryScanner (AST static analysis)
│   ├── document_loader.py     # LlamaIndex file loader
│   ├── code_splitter.py       # SentenceSplitter chunking
│   └── vector_store.py        # VectorStoreIndex builder
│
├── database/                  # Persistence layer
│   ├── connection.py          # SQLite engine + SessionLocal
│   ├── models.py              # ORM models: Incident, AgentTrace, FeatureProposal
│   └── crud.py                # Save + read operations
│
├── evaluation/
│   └── ragas_eval.py          # Ragas Faithfulness + Answer Relevancy scoring
│
├── dashboard/
│   └── app.py                 # Streamlit dashboard (3-page UI)
│
├── payment/                   # Demo target module for testing
│   ├── processor.py           # PaymentProcessor (intentional bug for demo)
│   └── exceptions.py          # Custom validation exceptions
│
├── tests/
│   └── test_patch.py          # 11 pytest assertions for patch validation
│
├── demo_vector_search.py      # Standalone semantic search demo script
├── main.py                    # Pipeline entry point
├── requirements.txt           # All Python dependencies
├── .env.example               # API key template
├── .gitignore
└── README.md

``` 
---

## ⚙️ Installation & Setup

### Prerequisites

- Python 3.12+
- [Ollama](https://ollama.com) installed and running locally
- Google Gemini API key (free tier)
- Git

### Step 1 — Clone the Repository

```bash
git clone https://github.com/ArindamDeka09/Nexus_Ops.git
cd Nexus_Ops
```

### Step 2 — Create Virtual Environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### Step 3 — Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4 — Pull Ollama Model

```bash
ollama pull llama3.2
```

Verify it works:
```bash
ollama run llama3.2 "Say hello in one sentence."
```

### Step 5 — Configure Environment Variables

```bash
cp .env.example .env
```

Open `.env` and fill in your keys:

```env
GEMINI_API_KEY=your_google_gemini_api_key_here
OLLAMA_BASE_URL=http://localhost:11434
```

### Step 6 — Initialise the Database

```bash
python -c "from database.connection import init_db; init_db()"
```

This creates `nexus_ops.db` in the project root with the three telemetry tables.

---

## 🚀 Running the Project

### Option A — Streamlit Dashboard (Recommended)

```bash
streamlit run dashboard/app.py
```

Open your browser at **http://localhost:8501**

The dashboard has three pages:
- **🚀 Run Pipeline** — Manual report or Auto-Scan repository mode
- **🗄️ Historical Telemetry Logs** — Browse all archived incidents from SQLite
- **🔍 Semantic Search** — Live vector search over any codebase

### Option B — Terminal Pipeline

```bash
python main.py
```

This runs the full 6-stage pipeline against the built-in payment module demo case and prints the complete anomaly report to terminal.

### Option C — Standalone Semantic Search Demo

```bash
python demo_vector_search.py
```

Demonstrates LlamaIndex embedding and cosine similarity retrieval live in the terminal — useful for showcasing the semantic search layer independently.

---

## 🎯 How to Use: Auto-Scan Mode

1. Launch the Streamlit dashboard
2. Select **Auto-Scan Repository** mode
3. Enter the **full path** to any Python project on your machine
   - Example: `D:/my_python_project`
4. Click **Scan & Fix**
5. The system will:
   - Run AST analysis across all `.py` files
   - If bugs are found → launch the full 6-stage repair pipeline
   - If codebase is clean → skip the repair swarm and generate feature proposals
6. Review results in the **Bug Resolutions**, **Feature Proposals**, **Ragas Scores**, and **Full Report** tabs
7. Switch to **Semantic Search** — the path auto-syncs from your last scan

---

## 🧪 Running the Test Suite

```bash
python -m pytest tests/test_patch.py -v
```

Expected output — 11 tests covering:
- Null check validation
- Type error regression guard
- Valid payment processing
- Fee calculation accuracy
- Transaction ID generation
- Edge cases: zero amount, negative amount, string injection, unsupported currency, multi-currency

---

## 📊 Database Schema

```text
nexus_ops.db
├── incidents          — One record per pipeline run
│   ├── id (PK)
│   ├── created_at
│   ├── issue_description
│   ├── category / priority / complexity
│   ├── root_cause_analysis
│   ├── draft_fix
│   ├── audit_verdict / tests_passed
│   ├── ragas_faithfulness / ragas_relevancy
│   └── final_report
│
├── agent_traces       — One record per agent execution step
│   ├── id (PK)
│   ├── incident_id (FK → incidents.id)
│   ├── agent_role
│   ├── stage
│   ├── output_text
│   └── iteration
│
└── feature_proposals  — Architectural enhancement proposals
    ├── id (PK)
    ├── incident_id (FK → incidents.id)
    ├── title / target_file / effort / description
    └── status (pending / approved / dismissed)


---

```

## 🔬 System Evaluation

Nexus Ops uses **Ragas** (LLM-as-a-Judge) to mathematically evaluate every generated fix:

| Metric | What It Measures | Target |
|---|---|---|
| **Faithfulness** | Is the fix grounded in retrieved code context? (prevents hallucination) | > 0.75 |
| **Answer Relevancy** | Is the fix the most direct, minimal solution? (prevents over-engineering) | > 0.70 |

Both metrics are scored on a **0.0 to 1.0 scale** using the local `llama3.2` model as the judge — no cloud API needed for evaluation.

---

## 🔭 Future Scope

- **CI/CD Integration** — GitHub Actions hook to trigger Nexus Ops on every pull request
- **Predictive Self-Healing** — Use historical agent trace embeddings to detect failure patterns before crashes occur
- **Multi-Language Support** — Extend the AST scanner to JavaScript, TypeScript, and Java
- **SaaS Deployment** — Package as an API service for SMEs requiring autonomous 24/7 code monitoring
- **Persistent Vector Store** — Swap in-memory LlamaIndex index for Qdrant or ChromaDB for large enterprise codebases
- **Human-in-the-Loop UI** — Add approve/reject patch controls before deployment in production environments

---

## 📚 References & Credits

- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [CrewAI Documentation](https://docs.crewai.com)
- [DSPy: Compiling Declarative Language Model Calls](https://github.com/stanfordnlp/dspy)
- [LlamaIndex Documentation](https://docs.llamaindex.ai)
- [Ragas: Evaluation for RAG Pipelines](https://docs.ragas.io)
- [Ollama — Run LLMs Locally](https://ollama.com)
- [Sentence Transformers — all-MiniLM-L6-v2](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2)
- [Streamlit Documentation](https://docs.streamlit.io)

---

## 👤 Author

**Arindam Deka**
- 🎓 Bachelor of Computer Applications (BCA) — Final Year
- 📧 GitHub: [@ArindamDeka09](https://github.com/ArindamDeka09)
- 🏫 Final Year Project — Semester VI

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

<div align="center">

*Built with Python, LangGraph, CrewAI, Ollama, and LlamaIndex*
*as a BCA Final Year Project demonstrating autonomous agentic AI engineering.*

⭐ **Star this repo if you found it useful!**

</div>
