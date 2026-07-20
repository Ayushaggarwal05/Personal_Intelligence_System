from typing import List
from sqlalchemy.orm import Session
from app.database.repositories.base_repository import SQLiteRepository
from app.database.models.chat_history import ChatHistory

class ChatRepository(SQLiteRepository[ChatHistory]):
    def __init__(self, db: Session):
        super().__init__(db, ChatHistory)

    def list_by_project(self, project_id: str, limit: int = 50) -> List[ChatHistory]:
        """Fetches the latest conversations logged for a project."""
        return self.db.query(self.model).filter(
            self.model.project_id == project_id
        ).order_by(self.model.timestamp.desc()).limit(limit).all()

    def clear_project_history(self, project_id: str):
        """Clears all chat transcripts associated with a project."""
        self.db.query(self.model).filter(self.model.project_id == project_id).delete()
        self.db.commit()

    def prune_old_messages(self, project_id: str, max_messages: int = 20):
        """Purges old chat records for a project workspace beyond the rolling max limit."""
        subquery = self.db.query(self.model.id).filter(
            self.model.project_id == project_id
        ).order_by(self.model.timestamp.desc()).offset(max_messages).all()
        
        if subquery:
            ids_to_delete = [item.id for item in subquery]
            self.db.query(self.model).filter(self.model.id.in_(ids_to_delete)).delete(synchronize_session=False)
            self.db.commit()
