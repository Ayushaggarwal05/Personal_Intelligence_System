from sqlalchemy.orm import Session
from app.database.repositories.chat_repository import ChatRepository
from app.database.repositories.project_repository import ProjectRepository
from app.agents.memory_agent import MemoryAgent
from app.core.exceptions import ProjectNotFoundException
from typing import List, Dict, Any

class MemoryService:
    """Business layer managing conversation history tracking, statistics logs, and weak areas caching."""
    def __init__(self, db: Session):
        self.db = db
        self.chat_repo = ChatRepository(db)
        self.project_repo = ProjectRepository(db)
        self.memory_agent = MemoryAgent(db)

    def list_history(self, project_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Retrieves formatted chat history list for a project."""
        project = self.project_repo.get_by_id(project_id)
        if not project:
            raise ProjectNotFoundException(project_id)
            
        history = self.chat_repo.list_by_project(project_id, limit=limit)
        return [
            {
                "id": h.id,
                "role": h.role,
                "content": h.content,
                "timestamp": h.timestamp
            } for h in history
        ]

    def clear_history(self, project_id: str):
        """Clears all conversation transcripts logged for a project."""
        project = self.project_repo.get_by_id(project_id)
        if not project:
            raise ProjectNotFoundException(project_id)
        self.chat_repo.clear_project_history(project_id)

    def get_weak_topics(self, project_id: str) -> List[str]:
        """Identifies developer's frequently missed topic keywords across interviews."""
        project = self.project_repo.get_by_id(project_id)
        if not project:
            raise ProjectNotFoundException(project_id)
        return self.memory_agent.extract_user_weak_areas(project_id)

    def get_frequently_discussed_topics(self, project_id: str, limit: int = 5) -> List[str]:
        """Extracts top occurring keywords from user messages logged in SQLite."""
        history = self.chat_repo.list_by_project(project_id, limit=100)
        
        words_count = {}
        stop_words = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "my", "is", "how", "what", "explain"}
        
        for h in history:
            if h.role == "user":
                words = h.content.lower().split()
                for w in words:
                    # Clean punctuation
                    w_clean = "".join(char for char in w if char.isalnum())
                    if w_clean and w_clean not in stop_words and len(w_clean) > 3:
                        words_count[w_clean] = words_count.get(w_clean, 0) + 1
                        
        sorted_words = sorted(words_count.items(), key=lambda x: x[1], reverse=True)
        return [w[0] for w in sorted_words][:limit]
