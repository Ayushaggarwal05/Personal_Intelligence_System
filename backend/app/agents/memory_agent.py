from sqlalchemy.orm import Session
from app.database.repositories.chat_repository import ChatRepository
from app.database.repositories.interview_repository import InterviewRepository, InterviewQARepository
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
        self.interview_repo = InterviewRepository(db)
        self.qa_repo = InterviewQARepository(db)

    def record_chat_message(self, project_id: str, role: str, content: str) -> ChatHistory:
        """Saves a conversation dialog message to SQLite history."""
        msg = ChatHistory(
            id=str(uuid.uuid4()),
            project_id=project_id,
            role=role,
            content=content,
            timestamp=get_utc_now()
        )
        return self.chat_repo.create(msg)

    def get_conversation_context(self, project_id: str, limit: int = 10) -> str:
        """Retrieves and formats latest dialog messages as formatted text context."""
        history = self.chat_repo.list_by_project(project_id, limit=limit)
        # Reverse to get chronological order
        history.reverse()
        
        lines = []
        for h in history:
            lines.append(f"{h.role.upper()}: {h.content}")
            
        return "\n".join(lines)

    def extract_user_weak_areas(self, project_id: str) -> List[str]:
        """Parses previous interview scorecard evaluations to identify frequently missing keywords."""
        interviews = self.interview_repo.list_by_project(project_id)
        
        missing_kw_counts = {}
        for iv in interviews:
            qas = self.qa_repo.list_by_session(iv.id)
            for qa in qas:
                if qa.scorecard:
                    try:
                        scorecard = json.loads(qa.scorecard)
                        for kw in scorecard.get("missing_keywords", []):
                            kw_clean = kw.lower().strip()
                            missing_kw_counts[kw_clean] = missing_kw_counts.get(kw_clean, 0) + 1
                    except Exception:
                        continue
                        
        # Sort and return keywords that are missing most frequently (at least once)
        sorted_kws = sorted(missing_kw_counts.items(), key=lambda x: x[1], reverse=True)
        return [kw[0] for kw in sorted_kws if kw[1] > 0]
