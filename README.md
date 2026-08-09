# Personal Engineering Intelligence System (PEIS)

PEIS is a production-grade, local-first retrieval and hybrid agent system designed to act as an AI engineering memory on your computer. It indexes your local workspaces, understands project structure via static analysis (AST parsing), and helps you prepare for interviews with dynamic, progressive learning follow-up questions tailored to your code.

---

## Architecture Flow

```mermaid
┌────────────────────────────────────────────────────────┐
│               User Local Workspace                    │
│   (Source of Truth: Python, TS, JS, PDFs, Markdown)    │
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│               Python Tool Layer                        │
│   (Deterministic: File Watcher, AST Parser, Hashing)    │
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│               Intelligence Layer                       │
│    (Metadata Cache: SQLite  &  Embeddings: LanceDB)    │
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│             Deterministic Orchestrator                 │
│      (Python: WorkflowEngine & _classify_intent)       │
└──────────────────────────┬─────────────────────────────┘
                           │
            ┌──────────────┼──────────────┐
            ▼              ▼              ▼
     ┌─────────────┐┌─────────────┐┌─────────────┐
     │ProjectAgent ││DiagramAgent ││InterviewAgent│
     │  (Chat &    ││  (Mermaid   ││ (Follow-up  │
     │ Explainer)  ││ Diagrams)   ││ Questions)  │
     └──────┬──────┘└──────┬──────┘└──────┬──────┘
            └──────────────┼──────────────┘
                           ▼
 ┌────────────────────────────────────────────────────────┐
 │                   Model Router                         │
 │      (Ollama Local  /  Cloud LLMs: Gemini, OpenAI)     │
 └──────────────────────────┬─────────────────────────────┘
                           │
                           ▼
 ┌────────────────────────────────────────────────────────┐
 │             Interactive React UI                       │
 │      (Chat Window, Diagrams Canvas, Settings Panel)    │
 └────────────────────────────────────────────────────────┘
```

---

## Features

- **Workspace Intelligence & Change Detection**: Fast file hashing (SHA-256) and directory tracking to re-index changed files only.
- **Static AST Code Parsing**: Extracts functions, class definitions, imports, dependencies, API endpoints, and database models from files (Python, JS, TS).
- **Progressive Learning Follow-up Questions**: Generates dynamic, codebase-specific progressive study questions after every chat explanation to guide study prep.
- **Rolling Context Memory**: Limits raw conversational logs at a rolling 20 messages per workspace project in SQLite to prevent database bloat and keep prompt payloads clean.
- **Real-time Mermaid Visualization**: Auto-generates system architecture, database ERD, and call sequence flowcharts.
- **Hybrid Semantic Engine**: Merges dense vector searches with relational metadata query filters.

---

## Tech Stack

### Frontend

- React, Vite, TypeScript
- Tailwind CSS & shadcn/ui
- Mermaid.js (Interactive Diagrams)
- React Markdown

### Backend

- FastAPI & Python
- SQLite (Relational Metadata Manifest & Chat Memory)
- LanceDB (Local Embeddings Vector Index)
- Model Router (Interchangeable Cloud/Local APIs)

---

## Project Structure

```
MyProjectPro/
│
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── api/                  # FastAPI Routes (chat, workspace, search, diagrams, settings)
│   │   ├── orchestrator/         # Brain (WorkflowEngine, ModelRouter)
│   │   ├── agents/               # AI Agents (ProjectAgent, InterviewAgent)
│   │   ├── tools/                # Pure Python utilities (AST, Filesystem, Diagram Gen)
│   │   ├── services/             # Core business logic Layer (Workspace, Search, PromptLoader)
│   │   ├── indexing/             # Scanner, watcher & incremental engine
│   │   ├── memory/               # Vector DB (LanceDB) and System Cache Management
│   │   └── database/             # SQLite session, repositories & schemas
│   │
│   ├── storage/                  # Local cache, logs & diagrams
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── components/           # Sidebar, ChatWindow, DiagramViewer & Settings
│   │   └── App.tsx               # Main Grid & Navigation Layout
│   └── package.json
│
├── ARCHITECTURE.md               # Visual guides, database schemas and workflows
├── PRD.md                        # Core product requirements and visions
├── RULES.md                      # Development rules and architectural rules
└── memory.md                     # Completed features, RAM optimizations & log
```

---

## Installation & Setup

### 1. Pre-requisites

Ensure you have Python 3.10+ and Node.js 18+ installed on your system.

### 2. Backend Setup

```bash
# Navigate to backend directory
cd MyProjectPro/backend

# Create virtual environment and install dependencies
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt

# Run FastAPI Server
uvicorn app.main:create_app --reload --port 8000
```

### 3. Frontend Setup

```bash
cd ../frontend

# Install dependencies
npm install

# Run Vite Local Development Server
npm run dev
```

---

## Running Integration Tests

To run the orchestration workflow test suite:

```bash
python backend/tests/test_orchestration.py
```

---

## Why PEIS?

Unlike general AI chatbots that require you to copy-paste snippets or upload entire projects to cloud servers, PEIS is built on local-first principles. It ensures your proprietary code remains on your machine while organizing its derived data into a structured knowledge base. It targets the direct developer workflow—serving not just as an editor plugin, but as a long-term engineering mentor.
