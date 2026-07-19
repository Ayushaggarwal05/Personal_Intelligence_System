from sqlalchemy.orm import Session
from app.database.models.project import Project
from typing import Optional

class KnowledgeStore:
    """Retrieves high-level indexed project metadata details from SQLite database."""
    def __init__(self, db: Session):
        self.db = db

    def get_project_profile(self, project_id: str) -> Optional[dict]:
        """Fetches language framework profiles for a project."""
        project = self.db.query(Project).filter(Project.id == project_id).first()
        if not project:
            return None
        return {
            "id": project.id,
            "name": project.name,
            "path": project.path,
            "framework": project.framework,
            "database": project.database_type,
            "summary": project.summary
        }
