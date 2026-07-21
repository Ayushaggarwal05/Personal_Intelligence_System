from typing import List
from sqlalchemy.orm import Session
from app.database.repositories.base_repository import SQLiteRepository
from app.database.models.symbol import Symbol
from app.database.models.file import File

class SymbolRepository(SQLiteRepository[Symbol]):
    def __init__(self, db: Session):
        super().__init__(db, Symbol)

    def list_by_file(self, file_id: str) -> List[Symbol]:
        """Lists all AST symbols extracted from a file."""
        return self.db.query(self.model).filter(self.model.file_id == file_id).all()

    def search_in_project(self, project_id: str, search_query: str, limit: int = 20) -> List[Symbol]:
        """Searches for symbols matching a keyword name, signature, or file path within a project."""
        query_str = search_query.strip()
        if not query_str:
            return self.db.query(self.model).join(File, self.model.file_id == File.id).filter(File.project_id == project_id).limit(limit).all()
            
        return self.db.query(self.model).join(File, self.model.file_id == File.id).filter(
            File.project_id == project_id,
            (self.model.name.like(f"%{query_str}%")) | 
            (self.model.signature.like(f"%{query_str}%")) |
            (File.relative_path.like(f"%{query_str}%"))
        ).limit(limit).all()
