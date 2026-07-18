from typing import Optional
from sqlalchemy.orm import Session
from app.database.repositories.base_repository import SQLiteRepository
from app.database.models.project import Project

class ProjectRepository(SQLiteRepository[Project]):
    def __init__(self, db: Session):
        super().__init__(db, Project)

    def get_by_path(self, path: str) -> Optional[Project]:
        """Retrieves a project using its absolute workspace folder path."""
        return self.db.query(self.model).filter(self.model.path == path).first()
