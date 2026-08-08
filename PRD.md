# Product Requirements Document (PRD)

# Personal Engineering Intelligence System (PEIS)

**Tagline:** *Your local, privacy-first AI engineering memory and mock interview coach.*

---

# 1. Executive Summary & Vision

Software engineers frequently work across multiple projects over months or years. As time passes, they naturally lose context around architecture, implementation details, database design, APIs, configuration, and engineering decisions they once made.

The **Personal Engineering Intelligence System (PEIS)** is a **local-first AI engineering assistant** designed to solve this problem.

Instead of duplicating projects, PEIS continuously understands and indexes the developer's local workspace, builds an intelligence layer over it, and acts as a long-term engineering memory.

Its primary goal is to help developers quickly regain project context, understand their own code, generate architecture insights, visualize system designs, and confidently explain projects during technical interviews.
---

## Problem Statement

Engineers often struggle to recall implementation details, design decisions, and architectural reasoning for projects they built months or years ago. Traditional documentation quickly becomes outdated, making interview preparation, project maintenance, and knowledge retrieval time-consuming. PEIS solves this by continuously building an intelligent understanding of the developer's local workspace and providing accurate, context-aware engineering assistance.

---

# 2. Target Audience

* Software Engineers preparing for technical interviews.
* Freelancers and Contractors managing multiple client codebases.
* Developers returning to older projects.
* Students preparing project demonstrations or placements.
* Engineers wanting a personal AI knowledge system for their local development workspace.

---

# 3. Core Features

## Feature 1 — Workspace Intelligence & Incremental Indexing

PEIS continuously understands the developer's local workspace while avoiding unnecessary processing.

### Capabilities

* Incremental workspace scanning
* SHA-256 based change detection
* File hashing
* Workspace monitoring
* Automatic re-indexing of modified files only
* Multi-language project detection

### Supported Files

* Python
* JavaScript
* TypeScript
* Go
* Java
* C++
* Markdown
* PDF
* JSON
* YAML
* Configuration files

### Code Understanding

* AST Parsing
* Function extraction
* Class extraction
* Route detection
* Dependency detection
* API discovery
* Database schema extraction
* Module relationship analysis

---

## Feature 2 — Project Intelligence & Knowledge Generation

PEIS automatically understands projects and generates engineering knowledge.

### Generates

* Project Summary
* Technology Stack
* Module Overview
* Dependency Graph
* API Overview
* Database Overview
* Folder Structure Understanding
* Authentication Flow
* Design Decisions
* Engineering Trade-offs
* Implementation Notes

---

## Feature 3 — Progressive Learning Follow-up Questions

PEIS generates dynamic, codebase-specific progressive study questions to help you prepare for technical interviews based on your conversation context.

### Progressive Questioning

* Custom follow-up questions generated after every chat response.
* Deeply tied to the exact technology stack and files in the explanation context.
* Highlights potential design decisions and developer trade-offs.
* Promotes technical vocabulary practice and articulation improvement.

---

## Feature 4 — Rolling Context Memory

PEIS logs conversation messages and maintains a rolling message history limit to keep the prompt payloads clean and memory footprint small.

### Rolling Retention

* Automatically parses chat query intent to determine technical substance.
* Records important queries to local SQLite history (e.g. system design questions, bug fixes, module interactions).
* Automatically prunes chat history, retaining a maximum of 20 rolling messages.
* Prevents context window bloat and keeps local inference speeds fast.

---

## Feature 5 — Real-Time Diagram Generation

Automatically visualizes project architecture.

### Supported Diagrams

* Architecture Diagram
* Database ER Diagram
* Authentication Flow
* API Flow
* Sequence Diagram
* Component Diagram
* Class Diagram

### Visualization

* Mermaid.js
* Interactive rendering
* Export support

---

## Feature 6 — Hybrid Retrieval Engine

PEIS provides intelligent project retrieval using multiple retrieval strategies.

### Retrieval Types

* Semantic Search
* Keyword Search
* Metadata Search
* File Search
* Hybrid Ranking

Example Queries

* Where is JWT implemented?
* Show Redis usage.
* Explain CrewFlow authentication.
* Compare CrewFlow and HomeDecor.
* Show all projects using Celery.

---

# 4. System Architecture

## Layer 1 — Source of Truth

The developer's local workspace remains the single source of truth.

PEIS never duplicates or modifies

* Source code
* Documentation
* PDFs
* Notes
* Images
* Configuration files

---

## Layer 2 — Python Tool Layer

Deterministic Python tools perform all workspace operations.

### Responsibilities

* File Search
* Folder Search
* File Reading
* AST Parsing
* Framework Detection
* Dependency Detection
* Git Metadata
* Project Detection
* Hash Generation
* Change Detection
* Workspace Watching
* Diagram Extraction
* Metadata Generation

The LLM never directly searches the local workspace.

---

## Layer 3 — Intelligence Layer

The Intelligence Layer stores derived knowledge rather than project files.

### SQLite Stores

* Projects
* File Metadata
* File Hashes
* Project Summaries
* Chat History
* Interview Notes
* Generated Diagrams
* Review Reports
* Cache

### Vector Store (LanceDB)

* Embeddings
* Semantic Index
* Retrieval Cache

---

## Layer 4 — Agent & Orchestration Layer

PEIS runs on a hybrid model combining deterministic Python workflow orchestrators and specialized generative AI agents.

### Deterministic Python Orchestrator (WorkflowEngine)

* Parses query intent (`_classify_intent()`) using fast heuristics and fallback LLM classification.
* Retrieves file content, parses symbols from database, and binds contextual prompts.
* Triggers workspace directory scanning, dependency checking, and change detection.

### Project Intelligence Agent (ProjectAgent)

* Explains codebase implementation details, modules, configuration files, and design choices.
* Compiles comprehensive system overviews and explains structural logic.

### Diagram Agent (DiagramAgent)

* Generates formatted Mermaid.js diagrams to visualize class relationships, schemas, and flows.

### Interview Agent (InterviewAgent)

* Generates progressive learning follow-up questions tailored to technical codebase contexts.

### Memory Agent (MemoryAgent)

* Saves user and assistant dialog messages to local SQLite database.
* Enforces a rolling 20-message message retention limit to keep context payload lightweight.

---

## Layer 5 — Model Router

The system intelligently routes requests to the most suitable model.

### Local Models

* Intent Classification
* Simple Summaries
* Lightweight Conversations

### Cloud Models

* Deep Reasoning
* Interview Generation
* Architecture Explanation
* Engineering Trade-offs

### Embedding Models

* Semantic Search
* Retrieval
* Knowledge Indexing

---

# 5. Technical Stack

## Backend

### Framework

* FastAPI
* Python

### Database

* SQLite
* LanceDB

### Indexing

* Incremental Indexing
* SHA-256 Hashing
* Workspace Watcher

### Parsing

* Python AST
* Tree-sitter
* Markdown Parser
* PDF Parser

### AI

* Local LLM
* Cloud LLM
* Embedding Models

### Orchestration

* Custom Workflow Engine
* Multi-Agent Architecture
* Model Router

---

## Frontend

### Framework

* React
* TypeScript
* Vite

### Routing

* React Router

### Styling

* Tailwind CSS
* shadcn/ui

### Visualization

* Mermaid.js
* React Markdown

---

# 6. Frontend Experience

PEIS follows an AI-first interface inspired by modern AI assistants.

## Primary Pages

### Chat

The primary workspace where users interact with PEIS.

Users can

* Ask engineering questions
* Generate interview preparation
* Compare projects
* Search code
* Explain architecture

A contextual side panel displays

* Project Overview
* Interview Notes
* Diagrams
* Reviews
* Files
* Memory

---

### Workspace

Displays all indexed engineering projects.

Each project includes

* Overview
* Technology Stack
* Architecture Summary
* Generated Diagrams
* Interview History
* Reviews
* Recent Conversations

---

# 7. Core Engineering Principles

PEIS is built around five core principles.

### Local-First

Projects remain on the user's machine.

### Source of Truth

Original project files are never duplicated.

### Deterministic Before AI

Python tools handle searching, parsing, indexing, and metadata extraction.

LLMs are used only for reasoning, explanation, interview generation, and natural language responses.

### Incremental Intelligence

Only changed files are reprocessed, making the system efficient, fast, and scalable. The system must avoid making a heavy load on memory and be as fast as possible when responding.

### Long-Term Engineering Memory

PEIS continuously evolves its understanding as projects evolve, becoming a persistent engineering knowledge companion rather than a one-time chatbot.

## Non-Goals

PEIS is not intended to:

- Replace IDEs.
- Replace GitHub.
- Modify source code automatically.
- Act as a general-purpose chatbot.
- Store duplicate copies of project files.
- require cloud connectivity for core functionality.

---

# 8. Technical Bottlenecks & Design Challenges

## 8.1 Directory Context Window Inflation vs. Subfolder Blindness

When a developer queries a specific codebase folder (e.g., *"tell me about the src folder"*), ASTA must provide the LLM with enough grounding structure to explain the folder accurately without triggering hallucinations or overloading CPU memory. This presents a critical technical tradeoff:

### The Bottleneck: Context Inflation
*   **The Problem:** For larger codebases, recursively listing all child files and directory trees inside a queried folder consumes massive context window space (often exceeding 1,000+ tokens).
*   **The Result:** Wastes local LLM context headroom, slows down CPU pre-fill inference times, and causes socket timeouts or truncated responses.

### The Tradeoff: Subfolder Blindness & Hallucinations
*   **The Problem:** If we optimize context by only sending the immediate Level-1 files and folder names (e.g., sending `📂 utils/` but omitting the files inside it), the LLM is left with a "blind spot." It knows a folder exists but is blind to its contents.
*   **The Result:** To provide a detailed explanation, the LLM falls back to its pre-trained memory and **hallucinates standard boilerplate files** (like guessing `src/utils/AppUtil.js` or `src/index.js` instead of seeing your real `motion.js` and `main.jsx`), destroying factual grounding.

### Resolution Strategy: Bounded 1-Level Directory Expansion

To resolve this scalability challenge, ASTA implements a **Bounded 1-Level Directory Expansion** mechanism in its RAG pipeline:
1.  **Strict 1-Level Depth Limit:** The Python backend maps and retrieves folder structures exactly 1 level deep relative to the queried directory, displaying only immediate child files and immediate subdirectories.
2.  **Capped File Listing:** For the queried directory or root level, the backend lists **only the first 3 files** as grounding samples, appending a count label (e.g., `... [+25 more files]`) for the remaining files to preserve memory.
3.  **Generic RAG Boundary Note:** For any nested subdirectories listed (folders marked with `📂`), their sub-contents are hidden. A strict, completely generic boundary instruction is appended to the context:
    `[RAG BOUNDARY NOTE: The contents of any nested subdirectories listed above (folders marked with 📂) are HIDDEN from your view. Do NOT assume, invent, or guess any file names inside those folders. Only explain their conceptual roles based on the folder name. If the user wants to explore their files, advise them to ask about that specific folder directly.]`
4.  **Result:** This guarantees that the total context payload for any folder query remains extremely lightweight (under 200 tokens) regardless of the codebase scale, while providing a clear logical boundary that prevents the LLM from making up nested file names.