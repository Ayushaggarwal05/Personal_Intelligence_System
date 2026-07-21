from typing import List, Optional
from sqlalchemy.orm import Session
from app.database.repositories.base_repository import SQLiteRepository
from app.database.models.file import File

class FileRepository(SQLiteRepository[File]):
    def __init__(self, db: Session):
        super().__init__(db, File)

    def get_by_relative_path(self, project_id: str, relative_path: str) -> Optional[File]:
        """Retrieves a file by its relative path inside a specific project workspace."""
        return self.db.query(self.model).filter(
            self.model.project_id == project_id,
            self.model.relative_path == relative_path
        ).first()

    def list_by_project(self, project_id: str) -> List[File]:
        """Lists all indexed files for a target project."""
        return self.db.query(self.model).filter(self.model.project_id == project_id).all()

    def search_by_keyword(self, project_id: str, keyword: str, limit: int = 5) -> List[File]:
        """Searches indexed files matching a keyword in their relative path."""
        kw_clean = keyword.strip()
        if not kw_clean:
            return []
        return self.db.query(self.model).filter(
            self.model.project_id == project_id,
            self.model.relative_path.like(f"%{kw_clean}%")
        ).limit(limit).all()
