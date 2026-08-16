# Personal Engineering Intelligence System (PEIS)

PEIS is a production-grade, local-first retrieval and hybrid agent system designed to act as an AI engineering memory on your computer. It indexes your local workspaces, understands project structure via static analysis (single-pass batch AST parsing), and helps you prepare for technical interviews with dynamic, progressive learning follow-up questions tailored to your code.

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
│ (Single-pass Batch AST Parser, File Watcher, Hashing)  │
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
     │(100% Local  ││ (Deterministic││ (Follow-up  │
     │ Chat & RAG) ││  Mermaid)   ││ Questions)  │
     └──────┬──────┘└──────┬──────┘└──────┬──────┘
            └──────────────┼──────────────┘
                           ▼
 ┌────────────────────────────────────────────────────────┐
 │                   Model Router                         │
 │  (Strict Local Ollama Chat | Scoped Cloud Diagrams)    │
 └──────────────────────────┬─────────────────────────────┘
                           │
                           ▼
 ┌────────────────────────────────────────────────────────┐
 │             Interactive React UI                       │
 │      (Chat Window, Diagrams Canvas, Settings Panel)    │
 └──────────────────────────┬─────────────────────────────┘
```

---

## Key Features & Capabilities

- **Strict Local-First Chat Privacy**: Chat, context retrieval, and technical explanation workflows run **100% strictly local** via Ollama (`qwen2.5:3b`). Zero silent cloud API fallbacks exist for chat.
- **Single-pass Batch AST Code Parsing**: Extracts functions, class definitions, imports, dependencies, API endpoints, and database models from files (Python, JS, TS). Uses single-pass batching for JS/TS files with automatic V8 memory cleanup to keep RAM usage lightweight.
- **Deterministic Architectural Diagrams (Diagram Canvas)**:
  - **Tab 1: Controller Sequence**: Traces the overall request lifecycle (Frontend UI ➔ Controller/Router ➔ Business Service ➔ SQLite Storage).
  - **Tab 2: Database Schema ER**: Generates a comprehensive, detailed Entity-Relationship schema containing all indexed model classes and fields.
  - **Tab 3: Backend Routes Flow**: Maps all backend API route endpoints, HTTP methods, and service handlers.
  - **Deterministic Generation (`temperature: 0.0`)**: Cloud API keys (Gemini `gemini-1.5-flash` / Groq `llama-3.1-8b-instant`) are scoped exclusively to diagram generation at `temperature: 0.0` for 100% consistent, hallucination-free output with zero dummy placeholders. Includes an AST-driven local fallback if rate limits occur.
- **Ollama Cold-Boot Warmup & Auto-Retry**: Automatically wakes Ollama when offline, executes a 1-token warmup ping to allocate model compute buffers, and preserves the full **`num_ctx: 8192`** memory context window.
- **Progressive Learning Follow-up Questions**: Generates dynamic, codebase-specific study questions after every technical explanation.
- **Rolling Context Memory**: Limits raw conversational logs at a rolling 20 messages per workspace project in SQLite to prevent database bloat.

---

## Tech Stack

### Frontend

- React, Vite, TypeScript
- Tailwind CSS & lucide-react
- Mermaid.js (Responsive Vector Architectural Canvas)
- React Markdown

### Backend

- FastAPI & Python 3.10+
- SQLite (Relational Metadata Manifest & Chat History)
- LanceDB (Local Vector Embeddings Engine)
- Model Router (Strict Local Chat Routing & Scoped Cloud Diagram APIs)

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
│   │   ├── agents/               # AI Agents (ProjectAgent, InterviewAgent, MemoryAgent)
│   │   ├── tools/                # Pure Python utilities (Batch AST, Filesystem, Diagram Generator)
│   │   ├── services/             # Core business logic Layer (Workspace, Search, PromptLoader)
│   │   ├── indexing/             # Scanner, watcher & incremental engine
│   │   ├── memory/               # Vector DB (LanceDB) and System Cache Management
│   │   └── database/             # SQLite session, repositories & schemas
│   │
│   ├── .env.example              # Environment configuration template
│   ├── storage/                  # Local cache, logs & diagrams
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── components/           # Sidebar, ChatWindow, DiagramViewer & SettingsDrawer
│   │   └── App.tsx               # Main Grid & Navigation Layout
│   └── package.json
│
├── ARCHITECTURE.md               # Detailed architectural specs & layer definitions
├── PRD.md                        # Product requirements and feature roadmap
├── RULES.md                      # Core development rules and local-first guidelines
└── memory.md                     # Completed features, optimizations & design decisions log
```

---

## Installation & Setup

### 1. Pre-requisites & Local LLM Setup

1. **Python 3.10+** & **Node.js 18+** installed on your system.
2. **Download & Install Ollama**:
   - Download Ollama from the official website: [**https://ollama.com/download**](https://ollama.com/download)
   - Install and launch Ollama on your system.
3. **Pull Qwen 2.5 3B Model**:
   ```bash
   ollama pull qwen2.5:3b
   ```

### 2. Environment Configuration

```bash
# Copy example environment configuration
copy .env.example backend\.env
```

### 3. Backend Setup

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

### 4. Frontend Setup

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

Unlike general cloud AI chatbots that require you to upload entire proprietary codebases to cloud servers, PEIS is built on strict local-first principles. Your source code and conversation logs remain 100% on your machine, while derived knowledge is indexed into a local, high-speed engineering memory tailored for developer understanding and technical interview preparation.
