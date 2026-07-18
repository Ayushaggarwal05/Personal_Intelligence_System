# Personal Engineering Intelligence System (PEIS)

PEIS is a production-grade, local-first retrieval and multi-agent system designed to act as an AI engineering memory on your computer. It indexes your local workspaces, understands project structure via static analysis (AST parsing), and helps you prepare for interviews with adaptive technical and behavioral mock sessions.

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
            ┌──────────────┴──────────────┐
            ▼                             ▼
 ┌─────────────────────┐       ┌─────────────────────┐
 │  Semantic Retrieval │       │ Keyword Retrieval   │
 │     (LanceDB)       │       │    (SQLite FTS5)    │
 └──────────┬──────────┘       └──────────┬──────────┘
            └──────────────┬──────────────┘
                           ▼
 ┌────────────────────────────────────────────────────────┐
 │                 Retrieval Agent                        │
 │           (Hybrid Search & Reranking)                  │
 └──────────────────────────┬─────────────────────────────┘
                           │
                           ▼
 ┌────────────────────────────────────────────────────────┐
 │               Multi-Agent Orchestrator                 │
 │ (Planner, Project Agent, Interview Agent, Review Agent)│
 └──────────────────────────┬─────────────────────────────┘
                           │
                           ▼
 ┌────────────────────────────────────────────────────────┐
 │                   Model Router                         │
 │      (Ollama Local  /  Cloud LLMs: Gemini, OpenAI)     │
 └──────────────────────────┬─────────────────────────────┘
                           │
                           ▼
 ┌────────────────────────────────────────────────────────┐
 │             Interactive React UI                       │
 │      (Chat Window, Mock Interview, Diagrams, Review)   │
 └────────────────────────────────────────────────────────┘
```

---

## Features

- **Workspace Intelligence & Change Detection**: Fast file hashing (SHA-256) and directory tracking to re-index changed files only.
- **Static AST Code Parsing**: Extracts functions, class definitions, imports, dependencies, API endpoints, and database models from files (Python, JS, TS, Go).
- **Project-Specific Mock Interview Coach**: Generates technical and HR mock questions specifically around your code and trade-offs.
- **Evaluation & Keyword Scorecard**: Evaluates answers, highlights missing concepts (e.g. JWT rotation, Connection Pooling), and generates senior-level model responses.
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
- SQLite (Relational Metadata Manifest)
- LanceDB (Local Embeddings Vector Index)
- Tree-sitter & AST parsers
- Model Router (Interchangeable Cloud/Local APIs)

---

## Project Structure

```
MyProjectPro/
│
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── api/                  # FastAPI Routes
│   │   ├── orchestrator/         # Brain (Planner, Workflow)
│   │   ├── agents/               # Multi-agent swarm (Workspace, Interview, Review)
│   │   ├── tools/                # Pure Python utilities (AST, Filesystem, Diagram Gen)
│   │   ├── services/             # Core business logic Layer
│   │   ├── indexing/             # Scanner, watcher & incremental engine
│   │   ├── memory/               # Knowledge and context handlers
│   │   ├── llm/                  # Model routing and templates
│   │   ├── database/             # SQLite session, repositories & schemas
│   │   └── tasks/                # Async jobs (scanning, generation)
│   │
│   ├── storage/                  # Local cache, logs & diagrams
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── app/                  # Routes, entry points & providers
│   │   ├── pages/                # Chat and Workspace pages
│   │   ├── components/           # Sidebar, panels (Interview, Diagram, Review) & UI
│   │   ├── features/             # Business features state logic
│   │   └── services/             # API client calls
│   └── package.json
│
├── architecture.md               # Visual guides, schemas and sequence charts
├── prd.readme                    # Core requirements, capabilities and goals
└── RULES.md                      # Development and design constraints
```

---

## How It Works

```
User Adds Workspace
        │
        ▼
Workspace Scanner
        │
        ▼
Project Detection (Frameworks, DBs)
        │
        ▼
Incremental Indexing (Hash Check)
        │
        ▼
Metadata Generation (AST Symbols)
        │
        ▼
Embedding Generation (Vectors)
        │
        ▼
Project Intelligence Ready
        │
        ▼
Workspace Changes Detected (Watcher)
        │
        ▼
Incremental Refresh (Re-indexing modified files only)
```

---

## Installation & Setup

### 1. Pre-requisites

Ensure you have Python 3.10+ and Node.js 18+ installed on your system.

### 2. Backend Setup

```bash
# Clone the repository
git clone <repo-url>
cd MyProjectPro/backend

# Install dependencies
pip install -r requirements.txt

# Create environmental configuration
copy .env.example .env

# Run FastAPI Server
uvicorn app.main:app --reload
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

## Why PEIS?

Unlike general AI chatbots that require you to copy-paste snippets or upload entire projects to cloud servers, PEIS is built on local-first principles. It ensures your proprietary code remain on your machine while organizing its derived data into a structured knowledge base. It targets the direct developer workflow—serving not just as an editor plugin, but as a long-term engineering mentor.
