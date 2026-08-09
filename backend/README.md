# ASTA / PEIS Backend — Personal Engineering Intelligence System

[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?style=flat-square&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python)](https://www.python.org/)
[![Ollama](https://img.shields.io/badge/Ollama-Local_LLM-black?style=flat-square)](https://ollama.ai/)
[![Qwen](https://img.shields.io/badge/Model-Qwen_2.5_3B-blueviolet?style=flat-square)](https://huggingface.co/Qwen)
[![SQLite](https://img.shields.io/badge/Database-SQLite-003B57?style=flat-square&logo=sqlite)](https://www.sqlite.org/)

The backend engine for **ASTA (Personal Engineering Intelligence System)** — a local-first engineering memory indexer, architectural explainer, and progressive study assistant.

---

## 🌟 Key Features & Capabilities

*   **⚡ Real-Time Word-by-Word Streaming**: Server-Sent Events (SSE) token streaming (`POST /api/chat/stream`) providing dynamic typewriter responses in the UI as local models generate text.
*   **🔥 10-Minute RAM Keep-Alive (`keep_alive: 10m`)**: Optimized model retention policy that keeps local LLMs loaded in memory during active chat sessions to eliminate cold-start delays, automatically unloading after 10 minutes of inactivity to free system RAM.
*   **🤖 Active AI Agents**: Specialized agent architecture (`ProjectAgent` for codebase explanations and `InterviewAgent` for follow-up study questions).
*   **🔍 AST Codebase Indexing & Parsing**: Native Abstract Syntax Tree (AST) parsers for Python and JavaScript/TypeScript extracting classes, method signatures, docstrings, and routes.
*   **🧹 Rolling Memory Retention**: Caps raw conversational logs at a rolling 20 messages per workspace project in SQLite to prevent database bloat and maintain lightweight prompt contexts.
*   **📊 Visual Diagram Generation**: Compiles database descriptions and metadata into visual Mermaid.js Entity-Relationship (ER) diagrams, sequence diagrams, and route flowcharts via the `DiagramAgent`.

---

## 📐 Architecture & Directory Overview

```text
backend/
├── app/
│   ├── api/            # FastAPI controllers (chat, workspace, search, diagrams, settings)
│   ├── orchestrator/   # Central Brain: WorkflowEngine & LLM ModelRouter
│   ├── agents/         # AI Agents (ProjectAgent, InterviewAgent, MemoryAgent)
│   ├── services/       # Business Logic Layer (WorkspaceService, SearchService, PromptLoaderService)
│   ├── tools/          # Deterministic Execution (AST Parsers, Git Diff, Binary Checks)
│   ├── indexing/       # Codebase Scanner, Incremental Indexer, and Background File Watcher
│   ├── memory/         # Vector DB (LanceDB) and System Cache Management
│   └── database/       # SQLAlchemy Models, Repositories, Schemas, and SQLite Session Connection
├── prompts/            # Agent System Prompt Templates (.txt)
├── tests/              # E2E Integration & System Test Suites
├── .env                # Runtime Environment Configuration
├── requirements.txt    # Python Package Dependencies
└── main.py             # Uvicorn Application Launcher (ASGI Factory)
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

4.  **Copy environment file and run API server**:
    ```bash
    copy .env.example .env
    python -m uvicorn app.main:create_app --reload --port 8000
    ```

---

## 🧪 Running Integration Tests

To run the orchestration workflow test suite:

```bash
python backend/tests/test_orchestration.py
```
