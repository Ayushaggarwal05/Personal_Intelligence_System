# Personal Engineering Intelligence System (PEIS) Developer Guide

PEIS is a local-first engineering memory and mock technical interview coach. This document outlines the system architecture, configuration parameters, API references, and WebSocket specifications for developers.

---

## 1. System Architecture

The project conforms to **Clean Architecture** and **SOLID design principles**, split into five decoupled layers:

```
┌────────────────────────────────────────────────────────┐
│                   Layer 6: API Routers                 │
│              (FastAPI, Uvicorn, WebSocket)             │
└───────────────────────────┬────────────────────────────┘
                            ▼
┌────────────────────────────────────────────────────────┐
│                 Layer 5: Workflows Engine              │
│          (Sequential execution of Agent swarms)        │
└───────────────────────────┬────────────────────────────┘
                            ▼
┌────────────────────────────────────────────────────────┐
│                   Layer 4: AI Agents                   │
│         (Planner, Project, Interview, Review)          │
└───────────────────────────┬────────────────────────────┘
                            ▼
┌────────────────────────────────────────────────────────┐
│                 Layer 3: Business Services             │
│        (WorkspaceService, MemoryService, Search)       │
└───────────────────────────┬────────────────────────────┘
                            ▼
┌────────────────────────────────────────────────────────┐
│             Layer 2: Database Repositories             │
│          (SQLAlchemy CRUD / LanceDB vectors)           │
└───────────────────────────┬────────────────────────────┘
                            ▼
┌────────────────────────────────────────────────────────┐
│                 Layer 1: Python Tools                  │
│       (ignore_parser, list_directory, AST parsers)     │
└────────────────────────────────────────────────────────┘
```

---

## 2. API Reference

All endpoints are hosted under the prefix `/api`.

### Workspace & Project Indexing
*   `POST /api/workspace/register`: Registers a local codebase path.
*   `DELETE /api/workspace/remove/{project_id}`: Unregisters workspace and stops watchers.
*   `GET /api/workspace/status/{project_id}`: Inspects background file watch status.
*   `GET /api/workspace/statistics/{project_id}`: Retrieves total indexed files and estimated token count.
*   `POST /api/projects/scan`: Triggers an incremental crawl scan matching `.gitignore` files.
*   `GET /api/projects/{project_id}/structure`: Compiles serializable folder tree and symbol mapping.

### Hybrid Search
*   `GET /api/search`: Query workspace using dense semantic matching + sparse keyword sorting.
    *   *Parameters*: `project_id`, `query`, `type` (filter files vs symbols), `limit`.
*   `GET /api/search/suggestions`: Endpoint autocomplete suggestions list.

### Mock Technical Interview
*   `POST /api/interview/start`: Creates a mock interview session and issues the first question.
*   `POST /api/interview/submit`: Submits the user's answer, grades technical keyword gaps, and generates the next question.

### Diagram Generation
*   `GET /api/diagrams/er/{project_id}`: Returns Mermaid.js Entity-Relationship schema markup.
*   `GET /api/diagrams/api-flow/{project_id}`: Returns Mermaid.js graph mapping FastAPI routes.
*   `GET /api/diagrams/sequence/{project_id}`: Returns sequence diagram illustrating request controller lifecycles.

---

## 3. WebSocket Streaming Specifications

*   **Endpoint**: `/api/ws`
*   **Protocol**:
    *   *Echo/Ping check*: Client sends `"ping"`, server replies `"pong"`.
    *   *Real-time token streaming*: Server streams LLM reply tokens using:
        ```json
        {
          "type": "token_stream",
          "stream_id": "uuid",
          "token": "word-chunk"
        }
        ```

---

## 4. Setup and Configuration

### Configuration Settings
Settings are loaded dynamically from environment variables or a local `.env` file:
*   `ACTIVE_LLM_PROVIDER`: `"local"` (Ollama), `"gemini"`, `"groq"`, `"openrouter"`.
*   `OLLAMA_MODEL`: defaults to `qwen2.5:3b-instruct`.
*   `DATABASE_URL`: SQLite local connection string.

### Run Verification Test Suites
Validate foundation layers, workspace scanners, and multi-agent workflows using:
```bash
python backend/tests/test_foundation.py
python backend/tests/test_workspace_intel.py
python backend/tests/test_ai_layer.py
python backend/tests/test_integration.py
```
