from sqlalchemy.orm import Session
from app.database.repositories.chat_repository import ChatRepository
from app.database.models.chat_history import ChatHistory
from app.utils.helpers import get_utc_now
import uuid
import json
from typing import List, Dict, Any

class MemoryAgent:
    """Memory Agent capturing conversation logs, caching topics, and tracking weak areas across sessions."""
    def __init__(self, db: Session):
        self.db = db
        self.chat_repo = ChatRepository(db)

    def is_important_technical_query(self, content: str) -> bool:
        """Determines if a chat query contains technical substance worthy of database preservation."""
        text = content.strip().lower()
        if not text:
            return False
            
        # 1. Skip simple greetings/social noise
        greetings = {"hi", "hello", "hey", "hola", "yo", "good morning", "good afternoon", "good evening", "how are you", "thanks", "thank you"}
        if text in greetings or any(text == g for g in greetings):
            return False
            
        # 2. Check for short noise inputs
        if len(text) <= 8 and not any(kw in text for kw in {"code", "api", "db", "git", "run", "bug", "fix", "ast"}):
            return False
            
        # 3. Must contain at least one technical or interrogative keyword
        tech_indicators = {
            "explain", "code", "file", "function", "class", "method", "variable", "route", "api",
            "database", "sql", "model", "query", "mismatch", "error", "bug", "fix", "setup", "run",
            "install", "architecture", "structure", "design", "how", "why", "where", "what", "who",
            "compare", "framework", "git", "diff", "patch", "agent", "orchestrator", "service", "core",
            "tools", "backend", "frontend", "work"
        }
        if any(indicator in text for indicator in tech_indicators):
            return True
            
        # If it doesn't match any indicator but is reasonably long, treat it as general query context
        if len(text) > 20:
            return True
            
        return False

    def record_chat_message(self, project_id: str, role: str, content: str) -> ChatHistory:
        """Saves a conversation dialog message to SQLite history and prunes old logs."""
        msg = ChatHistory(
            id=str(uuid.uuid4()),
            project_id=project_id,
            role=role,
            content=content,
            timestamp=get_utc_now()
        )
        created = self.chat_repo.create(msg)
        # Enforce rolling retention limit (keep max 20 messages)
        self.chat_repo.prune_old_messages(project_id, max_messages=20)
        return created

    def get_conversation_context(self, project_id: str, limit: int = 10) -> str:
        """Retrieves and formats latest dialog messages as formatted text context."""
        history = self.chat_repo.list_by_project(project_id, limit=limit)
        # Reverse to get chronological order
        history.reverse()
        
        lines = []
        for h in history:
            lines.append(f"{h.role.upper()}: {h.content}")
            
        return "\n".join(lines)


