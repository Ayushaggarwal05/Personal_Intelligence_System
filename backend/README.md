# ASTA / PEIS Backend — Personal Engineering Intelligence System

[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?style=flat-square&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python)](https://www.python.org/)
[![Ollama](https://img.shields.io/badge/Ollama-Local_LLM-black?style=flat-square)](https://ollama.ai/)
[![Qwen](https://img.shields.io/badge/Model-Qwen_2.5_3B-blueviolet?style=flat-square)](https://huggingface.co/Qwen)
[![SQLite](https://img.shields.io/badge/Database-SQLite-003B57?style=flat-square&logo=sqlite)](https://www.sqlite.org/)

The backend engine for **PEIS (Personal Engineering Intelligence System)** — a local-first engineering memory indexer, architectural explainer, and progressive study assistant.

---

## 🌟 Key Features & Capabilities

*   **🔒 Strict Local-First Privacy**: Chat, RAG context retrieval, and memory run **100% strictly local** via Ollama (`qwen2.5:3b`). Zero silent cloud fallbacks exist for chat.
*   **⚡ Single-Pass Batch AST Indexing**: Native Abstract Syntax Tree (AST) parsers for Python and JavaScript/TypeScript (`ast_parser.js`). Batch-executes JS/TS parsing in a single pass with immediate Node process exit to free V8 RAM for Ollama inference.
*   **🔥 Ollama Cold-Boot Warmup & Auto-Retry**: Automatically launches Ollama when offline, runs a 1-token pre-flight warmup ping (`"hi"`), and preserves the full **`num_ctx: 8192`** memory context window.
*   **🎨 Deterministic Architectural Diagrams**: Generates 100% deterministic (`temperature: 0.0`) Mermaid.js diagrams using scoped Gemini (`gemini-1.5-flash`) or Groq (`llama-3.1-8b-instant`) API keys. Includes an AST-driven fallback if rate limits (HTTP 429) occur.
*   **⚡ Real-Time SSE Token Streaming**: Server-Sent Events (SSE) token streaming (`POST /api/chat/stream`) providing dynamic typewriter responses in the UI as local models generate text.
*   **🤖 Specialized AI Agents**: `ProjectAgent` (codebase explanations), `InterviewAgent` (progressive study follow-ups), and `MemoryAgent` (rolling 20-message chat history).

---

## 📐 Architecture & Directory Overview

```text
backend/
├── app/
│   ├── api/            # FastAPI controllers (chat, workspace, search, diagrams, settings, memory)
│   ├── orchestrator/   # Central Brain: WorkflowEngine & ModelRouter
│   ├── agents/         # AI Agents (ProjectAgent, InterviewAgent, MemoryAgent)
│   ├── services/       # Business Logic Layer (WorkspaceService, SearchService, PromptLoader)
│   ├── tools/          # Pure Python & Batch AST Parsers, Diagram Generator
│   ├── indexing/       # Codebase Scanner, Incremental Indexer, and Background File Watcher
│   ├── memory/         # Vector DB (LanceDB) and System Cache Management
│   └── database/       # SQLAlchemy Models, Repositories, Schemas, and SQLite Session Connection
├── prompts/            # Agent System Prompt Templates (.txt)
├── tests/              # E2E Integration & System Test Suites
├── .env.example        # Environment Configuration Template
├── .env                # Runtime Environment Configuration
├── requirements.txt    # Python Package Dependencies
└── main.py             # Uvicorn Application Launcher (ASGI Factory)
```

---

## ⚙️ Environment Configuration (`.env`)

Copy `.env.example` to `.env` in the `backend/` directory:

```env
# Active LLM Provider: "local" (Ollama)
# Chat & RAG run 100% locally on your machine.
ACTIVE_LLM_PROVIDER=local

# Local Ollama Configurations
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=qwen2.5:3b

# Cloud AI Provider Keys (Scoped EXCLUSIVELY for Diagram Generation)
GEMINI_API_KEY=
GROQ_API_KEY=

# System Log Level
LOG_LEVEL=INFO
```

---

## 🚀 Getting Started

### 1. Prerequisites
*   **Python 3.10+**
*   **Node.js 18+** (for single-pass batch JS/TS AST parsing)
*   **Ollama**: Installed and running locally on port 11434 (`http://localhost:11434`). Download from [**https://ollama.com/download**](https://ollama.com/download).
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

4.  **Copy environment template and run API server**:
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
