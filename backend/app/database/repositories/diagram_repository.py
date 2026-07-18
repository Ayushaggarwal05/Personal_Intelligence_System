from typing import List, Optional
from sqlalchemy.orm import Session
from app.database.repositories.base_repository import SQLiteRepository
from app.database.models.diagram import Diagram

class DiagramRepository(SQLiteRepository[Diagram]):
    def __init__(self, db: Session):
        super().__init__(db, Diagram)

    def get_by_project_and_type(self, project_id: str, diagram_type: str) -> Optional[Diagram]:
        """Retrieves a diagram for a project workspace by its specific type."""
        return self.db.query(self.model).filter(
            self.model.project_id == project_id,
            self.model.type == diagram_type
        ).first()

    def list_by_project(self, project_id: str) -> List[Diagram]:
        """Lists all diagrams generated for a project."""
        return self.db.query(self.model).filter(self.model.project_id == project_id).all()
