# RULES.md

# Personal Engineering Intelligence System (PEIS)

This document defines the core engineering principles and architectural rules that govern the development of PEIS. Every new feature, agent, tool, or workflow should follow these principles.

---

# 1. Local-First Architecture

PEIS is a local-first application.

- User projects remain on the local machine.
- Core functionality must work without cloud services.
- Cloud models are optional enhancements, never requirements.

---

# 2. Source of Truth

The developer's workspace is the only source of truth.

PEIS must never:

- Duplicate source code.
- Modify project files automatically.
- Store unnecessary copies of user data.

PEIS stores only derived intelligence such as metadata, summaries, embeddings, diagrams, and interview material.

---

# 3. Deterministic Before AI

Never use an LLM for tasks that deterministic Python code can perform.

Python tools are responsible for:

- Searching files
- Reading files
- Parsing code
- Detecting frameworks
- Detecting dependencies
- AST analysis
- Hash generation
- Workspace monitoring
- Metadata extraction

LLMs are responsible only for:

- Reasoning
- Explanation
- Summarization
- Interview generation
- Engineering feedback
- Natural language responses

---

# 4. Tool-First Execution

Agents never directly access the filesystem.

Every workspace operation must go through the Python Tool Layer.

Example workflow:

User → Planner → Python Tools → Context → LLM → Response

---

# 5. Incremental Intelligence

PEIS should never rebuild project intelligence unnecessarily.

Whenever possible:

- Detect file changes.
- Compare hashes.
- Re-index only modified files.
- Preserve existing intelligence.

Efficiency is a core design goal.

---

# 6. Layer Separation

Every responsibility belongs to a specific layer.

Source of Truth
→ Python Tool Layer
→ Intelligence Layer
→ Agent Layer
→ Model Router
→ LLM

No layer should bypass another without a valid architectural reason.

---

# 7. Model Agnostic

PEIS must never depend on a single LLM provider.

The Model Router should allow interchangeable models for:

- Local inference
- Cloud reasoning
- Embeddings
- Future vision models

Changing models should not require changes to business logic.

---

# 8. Privacy by Design

User data belongs to the user.

- Projects remain local.
- Chats remain local by default.
- Embeddings remain local.
- Metadata remains local.
- No hidden data collection.

---

# 9. AI is an Assistant, Not an Authority

LLM outputs should be treated as suggestions.

When possible:

- Ground responses using indexed project knowledge.
- Validate outputs.
- Prefer deterministic facts over generated assumptions.

---

# 10. Single Responsibility

Each component should have one clear purpose.

Examples:

- Workspace Agent → Workspace state
- Retrieval Agent → Context retrieval
- Diagram Agent → Diagram generation
- Review Agent → Interview evaluation

Avoid combining unrelated responsibilities.

---

# 11. Keep the System Modular

Agents, tools, services, and models should be replaceable.

New functionality should extend the system instead of rewriting existing components.

---

# 12. Chat is the Primary Interface

The application is AI-first.

Users should interact primarily through natural language.

Traditional dashboards should remain secondary to conversational workflows.

---

# 13. Minimize Context Sent to LLMs

Never send an entire project to an LLM.

Always:

- Retrieve only relevant files.
- Build focused context.
- Keep prompts concise.
- Reduce token usage.

Smaller, targeted context produces better responses.

---

# 14. Intelligence Over Storage

PEIS stores knowledge, not projects.

Store:

- Metadata
- Summaries
- Embeddings
- Relationships
- Diagrams
- Interview history

Never duplicate the complete workspace.

---

# 15. Build for Long-Term Memory

Every interaction should strengthen the system's understanding.

PEIS should continuously evolve as projects evolve while preserving historical engineering knowledge.

---

# Guiding Philosophy

> Understand first. Retrieve second. Reason third.

PEIS is not a chatbot.

It is a long-term engineering intelligence system that helps developers understand, remember, and explain their own software with confidence.
