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

## Feature 3 — Project-Specific Mock Interview Coach

PEIS becomes an interview coach trained specifically on the developer's own projects.

### Technical Interview

* Project-specific questions
* Architecture questions
* Database questions
* API questions
* Design pattern questions
* Trade-off questions
* Follow-up questions

### HR Interview

* STAR-based questions
* Engineering decisions
* Team collaboration
* Challenges faced
* Optimization decisions

### Interactive Session

* Live interview mode
* Multi-round questioning
* Adaptive questioning
* Difficulty progression

---

## Feature 4 — Evaluation & Engineering Scorecard

PEIS evaluates interview answers using indexed project knowledge.

### Evaluation

* Keyword extraction
* Missing terminology detection
* Engineering concept grading
* Confidence score
* Project understanding score

### Feedback

Highlights missing concepts such as

* Connection Pooling
* JWT Rotation
* Caching
* RBAC
* Dependency Injection
* Optimistic Locking
* Rate Limiting
* Async Processing
* CQRS
* Event-driven Architecture

### Generates

* Senior-level model answer
* Improvement suggestions
* Missing concepts
* Better explanation examples

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

## Layer 4 — Agent Layer

A team of specialized AI agents coordinates all reasoning.

### Planner Agent

* Understands user intent
* Creates execution plan
* Selects required agents

### Workspace Agent

* Monitors projects
* Detects changes
* Maintains workspace index

### Project Intelligence Agent

* Understands project architecture
* Detects frameworks
* Generates project knowledge

### Retrieval Agent

* Retrieves relevant context
* Performs hybrid search

### Interview Coach Agent

* Generates technical interviews
* Generates HR interviews

### Diagram Agent

* Produces Mermaid diagrams
* Generates architecture flows

### Review Agent

* Evaluates interview answers
* Generates engineering feedback

### Reflection Agent

* Validates generated responses
* Improves answer quality

### Memory Agent

* Maintains long-term project memory
* Stores conversational context

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

Only changed files are reprocessed, making the system efficient and scalable.

### Long-Term Engineering Memory

PEIS continuously evolves its understanding as projects evolve, becoming a persistent engineering knowledge companion rather than a one-time chatbot.

## Non-Goals

PEIS is not intended to:

- Replace IDEs.
- Replace GitHub.
- Modify source code automatically.
- Act as a general-purpose chatbot.
- Store duplicate copies of project files.
- Require cloud connectivity for core functionality.