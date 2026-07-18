from typing import List, Optional
from sqlalchemy.orm import Session
from app.database.repositories.base_repository import SQLiteRepository
from app.database.models.interview import Interview, InterviewQA

class InterviewRepository(SQLiteRepository[Interview]):
    def __init__(self, db: Session):
        super().__init__(db, Interview)

    def list_by_project(self, project_id: str) -> List[Interview]:
        """Lists all interview sessions logged for a specific project."""
        return self.db.query(self.model).filter(self.model.project_id == project_id).all()


class InterviewQARepository(SQLiteRepository[InterviewQA]):
    def __init__(self, db: Session):
        super().__init__(db, InterviewQA)

    def list_by_session(self, interview_id: str) -> List[InterviewQA]:
        """Lists all questions and answers associated with a mock interview session ordered by timestamp."""
        return self.db.query(self.model).filter(
            self.model.interview_id == interview_id
        ).order_by(self.model.timestamp.asc()).all()
