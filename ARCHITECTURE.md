# Personal Engineering Intelligence System (PEIS) — Architecture Guide

This document describes the technical architecture, data flows, database schemas, and agent orchestration patterns for the **Personal Engineering Intelligence System (PEIS)**.

---

## 1. System Topology Overview

PEIS is structured into 5 logical layers to guarantee a local-first, privacy-respecting, and incremental engineering intelligence system.

```mermaid
graph TD
    %% Layer 1: Source of Truth
    subgraph L1 ["Layer 1: Source of Truth (Local Workspace)"]
        code[Codebases: PY, TS, JS, Go]
        docs[Docs: Markdown, PDFs]
        configs[Configs: JSON, YAML]
    end

    %% Layer 2: Python Tool Layer
    subgraph L2 ["Layer 2: Python Tool Layer (Deterministic)"]
        crawler[Workspace Scanner / Watcher]
        parsers[AST Parsers & Doc extractors]
        git_tool[Git History & Commit analyzer]
    end

    %% Layer 3: Intelligence Layer
    subgraph L3 ["Layer 3: Intelligence Layer (Metadata & Vectors)"]
        sqlite[(SQLite: Project AST, Hashes, Chat & Logs)]
        lancedb[(LanceDB: Code & Doc Vector Embeddings)]
    end

    %% Layer 4: Agent Layer
    subgraph L4 ["Layer 4: Agent Layer (Orchestration)"]
        planner[Planner Agent]
        workspace_a[Workspace Agent]
        project_a[Project Intel Agent]
        retrieval_a[Retrieval Agent]
        interview_a[Interview Coach Agent]
        diagram_a[Diagram Agent]
        review_a[Review Agent]
        reflection_a[Reflection Agent]
        memory_a[Memory Agent]
    end

    %% Layer 5: Model Router
    subgraph L5 ["Layer 5: Model Router (Inference API)"]
        router[Model Router]
        local_llm[Local LLM: Ollama/Llama.cpp]
        cloud_llm[Cloud LLM: Gemini/Groq/OpenAI]
    end

    %% Flow lines
    L1 -->|File Hashes / Reads| L2
    L2 -->|Update Hashes & AST| sqlite
    L2 -->|Write Embeddings| lancedb

    planner -->|Delegate tasks| workspace_a
    planner -->|Delegate tasks| project_a
    planner -->|Delegate tasks| retrieval_a
    planner -->|Delegate tasks| interview_a
    planner -->|Delegate tasks| diagram_a
    planner -->|Delegate tasks| review_a

    retrieval_a -->|Hybrid search| sqlite
    retrieval_a -->|Vector search| lancedb

    review_a -->|Refine feedback| reflection_a

    %% Model interaction
    L4 <-->|Reasoning requests| router
    router <-->|Local queries| local_llm
    router <-->|Heavy reasoning| cloud_llm
```

---

## 2. Component Layer Detail

### Layer 1: Source of Truth (Local Filesystem)

The system treats the developer’s local disk as read-only. No operations within PEIS modify, rename, or write back to code or configuration files under analysis. Files are read on-demand to perform parsing or retrieval.

### Layer 2: Python Tool Layer

Designed to act as a **deterministic barrier** before invoking AI reasoning. LLMs do not scrape directories or grep code directly.

- **Workspace Scanner / Watcher**: Traverses the root paths, generates SHA-256 hashes of individual files, and compares them with the SQLite manifest.
- **AST Parsers**: Uses standard Python `ast` and package dependencies (like `tree-sitter` for JavaScript/TypeScript/Go) to construct a structured declaration tree containing exports, imports, classes, functions, routes, and DB models.
- **Document Extractor**: Converts PDFs, markdown, and config settings to cleaned, uniform text snippets.

### Layer 3: Intelligence Layer

The local derived cache that feeds agents context.

- **SQLite Storage**: Houses relational structures (e.g. which project owns which files, structural relationships of functions, schemas, schemas history, mock interview logs).
- **Vector DB (LanceDB)**: Zero-dependency, serverless vector store stored alongside SQLite, queryable with low latency. Houses chunks of code, documentation, and user conversational embeddings.

### Layer 4: Agent Layer

A swarm of specialized agents executing tasks behind a **Planner Agent**:

1.  **Planner Agent**: The main orchestrator. It receives user inputs, designs an execution plan (e.g. _Index_ -> _Retrieve_ -> _Answer_), triggers relevant agents, and builds the final response.
2.  **Workspace Agent**: Executes scans, change detection, and coordinates file watchers.
3.  **Project Intelligence Agent**: Analyzes AST mappings to understand framework patterns, database choices, endpoints, and trade-offs.
4.  **Retrieval Agent**: Connects vector search (LanceDB) and keyword search (SQLite FTS5) into a unified hybrid retrieval list.
5.  **Interview Coach Agent**: Selects project technical and behavioral concepts and produces interactive mock questions.
6.  **Diagram Agent**: Generates flowcharts and entity relationship definitions formatted as Mermaid.js source strings.
7.  **Review Agent**: Performs semantic matching on the user’s interview answers, lists missing keywords, and compiles scores.
8.  **Reflection Agent**: Audits the generated answers and reviews against the database mappings to ensure zero hallucinations.
9.  **Memory Agent**: Keeps track of context windows and summarizes past dialog.

### Layer 5: Model Router

An interface abstraction module. Depending on task complexity:

- **Intent classification / code chunk indexing** is routed to lightweight local models (e.g. Llama-3-8B-Instruct via Ollama/Groq).
- **Architecture analysis / mock interview generation** is routed to advanced models (e.g. Gemini 1.5 Pro, GPT-4o).

---

## 3. Core Workflows

### Workflow A: Hash-Based Incremental Indexing

Runs automatically when a project is selected or when the file watcher fires.

```mermaid
sequenceDiagram
    autonumber
    participant UI as React Frontend
    participant WS as Workspace Agent (Layer 4)
    participant FS as Local Filesystem (Layer 1)
    participant DB as SQLite DB (Layer 3)
    participant TS as AST Tools (Layer 2)
    participant VDB as LanceDB (Layer 3)

    UI->>WS: Select Project Workspace
    WS->>FS: Crawl files and compute SHA-256 hashes
    WS->>DB: Query existing file metadata & hashes

    rect rgb(230, 245, 255)
        note over WS, VDB: Incremental Sync Evaluation Loop
        alt File is new or hash has changed
            WS->>TS: Read file & Extract AST (Classes/Methods/APIs)
            TS->>DB: Upsert file metadata & AST symbol tables
            TS->>VDB: Generate embeddings for code/text chunks & Upsert
        else File is unchanged
            WS->>DB: Update 'last_seen' timestamp only (Skip parsing)
        end
    end

    WS->>DB: Delete records of files no longer present in workspace
    WS->>UI: Return Indexing Status (Success, files processed)
```

---

### Workflow B: Mock Interview and Keyword Evaluation

Handles interactive technical preparation.

```mermaid
sequenceDiagram
    autonumber
    participant UI as React Frontend
    participant IA as Interview Coach Agent
    participant DB as SQLite (AST & Context)
    participant RA as Review Agent
    participant RE as Reflection Agent

    UI->>IA: Start Mock Interview
    IA->>DB: Pull API lists, DB Schemas, and Project Summaries
    IA->>UI: Generate & Present Project-Specific Interview Question
    UI->>IA: Submit User Response (Text / Transcript)

    IA->>RA: Pass Question, User Response, & Project Context
    RA->>RA: Extract response concepts & compare to project metadata
    RA->>RA: Identify missing concepts (e.g., JWT rotation, Connection Pooling)
    RA->>RA: Generate senior-level model answer

    RA->>RE: Request output verification
    RE->>RE: Check response against code files (verify keywords exist)
    RE-->>RA: Verification approved

    RA->>DB: Log Question, Answer, Score & Feedback
    RA->>UI: Return Scorecard (Keywords gap, model answer, rating)
```

---

## 4. Intelligence Layer Database Schema

Below is the SQLite relational schema that structures PEIS's derived intelligence.

```mermaid
erDiagram
    PROJECTS ||--o{ FILES : contains
    PROJECTS ||--o{ INTERVIEWS : tracks
    FILES ||--o{ SYMBOLS : declares
    INTERVIEWS ||--o{ INTERVIEW_QA : records

    PROJECTS {
        text id PK
        text name
        text path UK
        text framework
        text database_type
        text summary
        integer created_at
        integer updated_at
    }

    FILES {
        text id PK
        text project_id FK
        text relative_path
        text file_hash
        integer last_modified
        integer token_count
        text summary
    }

    SYMBOLS {
        text id PK
        text file_id FK
        text name
        text type "class | function | route | model"
        text signature
        text docstring
        integer line_start
        integer line_end
    }

    INTERVIEWS {
        text id PK
        text project_id FK
        text status "active | completed"
        integer score
        integer created_at
    }

    INTERVIEW_QA {
        text id PK
        text interview_id FK
        text question
        text user_answer
        text feedback_json "missing keywords, score, model answer"
        integer timestamp
    }
```

### Vector Store Schema (LanceDB)

Stored in `storage/cache/vector_store.db` with the following columns:

- `id`: String (UUID)
- `project_id`: String (FK to PROJECTS)
- `file_id`: String (FK to FILES)
- `chunk_index`: Integer
- `content`: String (Source code chunk or clean text)
- `vector`: Float32 Array (Dimensions: 384 for local or 1536/3072 for cloud embeddings)
- `type`: String (`code` or `docs`)

---

## 5. Directory Mapping and Orchestration Pipeline

When the React frontend issues a query, it hits `backend/app/main.py` which passes control through the **Orchestration Pipeline**:

1.  **FastAPI Router (`app/api/`)**: Dispatches the request.
2.  **Service Layer (`app/services/`)**: Pulls DB connections, sets up vector stores, and loads configurations.
3.  **Planner (`app/orchestrator/planner.py`)**: Receives request data and maps instructions:
    ```python
    # Logic abstraction of the Planner Agent
    plan = {
        "steps": [
            {"agent": "retrieval_agent", "action": "hybrid_search", "args": {"query": query}},
            {"agent": "reflection_agent", "action": "validate_context"},
            {"agent": "review_agent", "action": "score_response"}
        ]
    }
    ```
4.  **Agent Invocation (`app/agents/`)**: Executes the list sequentially or in parallel.
5.  **Model Router (`app/orchestrator/model_router.py`)**: Formulates the prompt template from `llm/prompts/` and posts request payload to the designated local or remote model endpoint.
6.  **Response Builder (`app/orchestrator/response_builder.py`)**: Packages the response structure to send back to the frontend Client.

## Project Lifecycle section

User adds Workspace
│
▼
Workspace Scanner
│
▼
Project Detection
│
▼
Incremental Indexing
│
▼
Metadata Generation
│
▼
Embedding Generation
│
▼
Project Intelligence
│
▼
Ready for Chat
│
▼
Workspace Changes
│
▼
Incremental Refresh
