# ASTA / PEIS Backend — Personal Engineering Intelligence System

[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?style=flat-square&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python)](https://www.python.org/)
[![Ollama](https://img.shields.io/badge/Ollama-Local_LLM-black?style=flat-square)](https://ollama.ai/)
[![Qwen](https://img.shields.io/badge/Model-Qwen_2.5_3B-blueviolet?style=flat-square)](https://huggingface.co/Qwen)
[![SQLite](https://img.shields.io/badge/Database-SQLite-003B57?style=flat-square&logo=sqlite)](https://www.sqlite.org/)

The backend engine for **ASTA (Personal Engineering Intelligence System)** — a local-first engineering memory indexer, architectural explainer, and adaptive mock technical interview coach.

---

## 🌟 Key Features & Capabilities

*   **⚡ Real-Time Word-by-Word Streaming**: Server-Sent Events (SSE) token streaming (`POST /api/chat/stream`) providing dynamic typewriter responses in the UI as local models generate text.
*   **🔥 10-Minute RAM Keep-Alive (`keep_alive: 10m`)**: Optimized model retention policy that keeps Qwen loaded in memory during active chat sessions to eliminate cold-start delays, automatically unloading after 10 minutes of inactivity to free system RAM.
*   **🤖 Multi-Agent Orchestration**: Modular multi-agent execution pipeline (`ProjectAgent`, `InterviewAgent`, `ReviewAgent`, `ReflectionAgent`, `MemoryAgent`, `DiagramAgent`, `PlannerAgent`).
*   **🔍 AST Codebase Indexing & Parsing**: Native Abstract Syntax Tree (AST) parsers for Python, JavaScript/TypeScript, and C++ extracting classes, method signatures, docstrings, and REST API routes.
*   **🐙 Git Commit Diff Analysis**: Extracts recent code modifications using `git show` patches so the Mock Interview Coach tests developers on their exact recent commits.
*   **🧹 Rolling Memory Retention**: Caps raw conversational logs at a rolling 20 messages per workspace project in SQLite to prevent database bloat, while permanently storing scorecards, weak/strong topics, and symbol metadata.
*   **📊 Visual Diagram Generation**: Compiles parsed codebase structures into visual Mermaid.js Entity-Relationship (ER) diagrams, sequence diagrams, and route flowcharts.

---

## 📐 Architecture & Directory Overview

```text
backend/
├── app/
│   ├── api/            # FastAPI controllers (chat, workspace, interview, review, diagrams, settings)
│   ├── orchestrator/   # Central Brain: WorkflowEngine & LLM ModelRouter
│   ├── agents/         # AI Agents (Project, Interview, Review, Reflection, Memory, Diagram, Planner)
│   ├── services/       # Business Logic Layer (Workspace, Memory, Interview, Search, PromptLoader)
│   ├── tools/          # Deterministic Execution (AST Parsers, Git Diff Patch, Binary Checks, Chunker)
│   ├── indexing/       # Codebase Scanner, Incremental Indexer, and Background File Watcher
│   ├── llm/            # Local Ollama, Gemini, and Groq Provider Adapters & Vector Embeddings Engine
│   ├── memory/         # Vector DB (LanceDB / Fallback) and System Cache Management
│   ├── database/       # SQLAlchemy Models, Repositories, Schemas, and SQLite Session Connection
│   ├── tasks/          # Asynchronous Background Worker Threads (Scanning, Embeddings, Diagrams)
│   └── core/           # Infrastructure Foundation (Settings, Security, Logging, Exceptions, WebSockets)
├── prompts/            # Agent System Prompt Templates (.txt)
├── tests/              # E2E Integration & System Test Suites
├── .env                # Runtime Environment Configuration
├── requirements.txt    # Python Package Dependencies
└── main.py             # Uvicorn Application Launcher
```

---

## ⚙️ Environment Configuration (`.env`)

Create or update your `.env` file in the `backend/` directory:

```env
# Application Metadata
PROJECT_NAME="ASTA Personal Engineering Intelligence System"
VERSION="1.0.0"
DEBUG=true

# Active LLM Provider ("local", "gemini", or "groq")
ACTIVE_LLM_PROVIDER=local

# Local Ollama Configurations
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=qwen2.5:3b

# Cloud AI Provider Keys (Optional overrides for DiagramAgent or Cloud Fallbacks)
GEMINI_API_KEY=
GROQ_API_KEY=

# Database Configuration
DATABASE_URL=sqlite:///./peis.db
```

---

## 🚀 Getting Started

### 1. Prerequisites
*   **Python 3.10+**
*   **Ollama**: Installed and running locally on port 11434 (`http://localhost:11434`).
*   **Qwen 2.5 Model**: Downloaded via Ollama:
    ```bash
    ollama pull qwen2.5:3b
    ```

### 2. Installation & Setup

1.  **Navigate to the backend directory**:
    ```bash
    cd backend
    ```

2.  **Create and activate a virtual environment**:
    ```bash
    python -m venv venv
    # On Windows:
    .\venv\Scripts\activate
    # On macOS/Linux:
    source venv/bin/activate
    ```

3.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Start the Uvicorn Backend Development Server**:
    ```bash
    python -m uvicorn app.main:create_app --reload --port 8000
    ```
    The server will start at **`http://localhost:8000`**. You can access interactive API documentation at `http://localhost:8000/docs`.

---

## 📡 API Endpoints Overview

| Category | Endpoint | Method | Description |
| :--- | :--- | :--- | :--- |
| **Chat** | `/api/chat/stream` | `POST` | Real-time word-by-word SSE token streaming response. |
| **Chat** | `/api/chat/query` | `POST` | Synchronous chat explanation response. |
| **Workspace** | `/api/workspace/register` | `POST` | Registers a local codebase path and triggers AST scanning. |
| **Workspace** | `/api/workspace/rescan` | `POST` | Triggers an incremental codebase index rescan. |
| **Interview** | `/api/interview/generate` | `POST` | Generates a project-tailored interview question using AST symbols and Git diffs. |
| **Review** | `/api/review/score` | `POST` | Grades developer interview answers (0–100 score, missing keywords, model answer). |
| **Diagrams** | `/api/diagrams/er` | `GET` | Compiles Mermaid.js Entity-Relationship diagram markup. |
| **Search** | `/api/search/query` | `GET` | Performs hybrid keyword-vector search across codebase chunks. |
| **Memory** | `/api/memory/weak-topics` | `GET` | Extracts developer's frequently missed interview technical topics. |
| **Settings** | `/api/settings/keys` | `POST` | Dynamically updates and saves Gemini/Groq API keys to `.env`. |

---

## 🧪 Running Automated Tests

Run the full system E2E integration test suite to verify database connections, agent pipelines, and API routes:

```bash
python backend/tests/test_integration.py
```

---

## 🔒 Security & Data Privacy

*   **100% Local Processing**: All code scanning, AST parsing, and chat queries execute locally on your machine using Ollama.
*   **Path Traversal Prevention**: File reads are validated through `is_safe_path` safeguards to ensure directory access never breaks workspace boundaries.
*   **Binary Safeguards**: Inspects the first 1024 bytes of files for null bytes to prevent non-text files from polluting the vector index.
