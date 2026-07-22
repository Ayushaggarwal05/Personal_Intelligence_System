# ASTA System Memory & Design Decisions

This document tracks the core architectural enhancements, design decisions, and future roadmap that govern the Personal Engineering Intelligence System (ASTA).

---

## 1. Key Improvements Completed

### 🚀 10-Minute RAM Keep-Alive (`keep_alive: 10m`)

- **What**: Eliminated the 20–30s cold-start loading delays during active user chat sessions.
- **How**: Passed `"keep_alive": "10m"` in Ollama request payloads. Qwen remains warm in RAM during active sessions and automatically unloads after 10 minutes of inactivity to free system resources.

### ⚡ Real-Time SSE Token Streaming

- **What**: Converted chat responses from slow page-waiting blocks into instant, word-by-word typewriter output.
- **How**: Refactored the backend `/api/chat/stream` API to return a FastAPI `StreamingResponse` yielding tokens, and updated the React frontend `ChatWindow.tsx` to consume the HTTP chunks progressively.

### 🔍 Dynamic File & Keyword RAG Retrieval

- **What**: Fixed LLM hallucinations where Qwen guessed or gave generic Django responses when asked about files (like `exceptions.py` or `checkout.py`).
- **How**: Programmed the retrieval layer to extract user query keywords, search `FileRepository` for physical paths, read the actual code snippet from disk, and inject it as direct prompt context.

### 🔄 Active Chat History Synchronization

- **What**: Resolved the "sudden error" where old topics (like Docker) bled into fresh chat windows.
- **How**: Shifted history tracking from database logs to the active React window messages state. If you refresh or open a new window, the context starts completely clean.

### 🎯 Qwen Bulleted Prompt Optimization
*   **What**: Stopped the local Qwen model from leaking system rules or repeating prompt directives in its final responses.
*   **How**: Restructured prompts using distinct Markdown sections (`# SYSTEM ROLE`, `# PROJECT CONTEXT`, `# USER QUERY`, `# INSTRUCTIONS`) and short, imperative bullet points that are easy for small models to follow.

### 📁 Recursive Monorepo Dependency Parsing
*   **What**: Enabled complete tech stack profiling and dependencies mapping for monorepos (where `requirements.txt` and `package.json` are inside nested folders like `./backend/` and `./frontend/` rather than the root).
*   **How**: Upgraded `detect_dependencies.py` to search recursively up to 3 levels deep, gathering and merging all library definitions to provide a complete picture of the stack to the LLM.

### 🎓 Unified Technical Interview Mentor Chat
*   **What**: Consolidated the separate `Architecture Explainer` and `Mock Interview Coach` tabs into a single, cohesive **Technical Interview Mentor** chat interface.
*   **How**: Removed the duplicate tab button in `App.tsx` and modified `project_agent.py` prompts to ALWAYS structure architectural answers in an interview-ready senior pitch format, including tech trade-off defenses and the top 3 likely follow-up recruiter questions.

### 📝 Chat Answer Evaluation RAG Integration
*   **What**: Integrated the previously idle `ReviewAgent` and `ReflectionAgent` backend pipelines directly into the main conversational chat interface to evaluate user responses.
*   **How**: Added check interceptors in `workflow.py`. If a query starts with `"Answer:"` or `"My response is:"`, it routes the message and the last asked question through the semantic grading logic to output an instant scorecard (score, matched terms, and gaps) directly in your chat stream.

### 🤝 Multi-Agent Question Delegation
*   **What**: Delegated mock follow-up questions generation to the specialized `InterviewAgent` instead of forcing the general `ProjectAgent` to do it.
*   **How**: Modified the conductor flow in `workflow.py`. The system first streams the technical pitch from `ProjectAgent`, then invokes `InterviewAgent.generate_chat_followup_questions` to design 3 highly-targeted technical questions about the explanation given, appending them directly to the client stream.

### 📚 Architecture Guide Alignment
*   **What**: Synchronized the technical design documentation with the active codebase improvements.
*   **How**: Replaced the obsolete Workflow B (separate Mock Interview UI) in `ARCHITECTURE.md` with the new unified Technical Interview Mentor sequence diagram, outlining Turn 1 (Explanation & Question generation) and Turn 2 (Inline scorecard evaluation).

### ⚡ Greeting Intent Interception & Stack Segregation
*   **What**: Bypassed agent RAG cycles for simple greetings to save system resources and segregated monorepo dependency libraries by stack.
*   **How**: Added string-matching greeting filters at the entry of workflows to return instant welcome template strings. Created `extract_dependencies_categorized` to separate package dependencies into Frontend and Backend layers, preventing Qwen from confusing React with SQLite and Django with Redux Toolkit.

### 🎭 Casual vs. Technical Query Classifier Routing
*   **What**: Resolved the issue where general chat messages (like "what are you doing") triggered full technical evaluations and follow-up questions.
*   **How**: Added `is_technical_query` to `PlannerAgent` using dynamic LLM intent classification. If classified as a casual query, the workflow conductor bypasses codebase token retrieval, disables follow-up questions, and instructs `ProjectAgent` to respond naturally without appending technical mock structures.

---

## 2. Best Decisions (Why Chat is Good Now)

1.  **Differentiating Context from Instructions**: Separating history, workspace data, and instruction blocks using strict Markdown boundaries prevented Qwen from getting confused.
2.  **Stateless History Sync**: Letting the frontend own the chat history payload kept the chatbot's memory 100% synchronized with what you actually see on screen.
3.  **Deterministic File Parsing**: Resolving files and symbols programmatically via Python _before_ passing them to Qwen ensured the local model only reasons about real codebase facts.

---

## 3. Future Improvements (What to Focus on Next)

- **Semantic Re-Ranking**: Further combine database symbol keywords and LanceDB semantic vectors to prioritize class and function structures.
- **Progressive Indexing Notifications**: Use the WebSocket tunnel to send real-time indexing percentages as large workspaces are scanned.
- **Interactive Score Trends**: Add a dashboard panel in the frontend showing interview score improvements and weak areas over time.
