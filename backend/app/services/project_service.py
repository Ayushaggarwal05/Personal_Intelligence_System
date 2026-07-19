from sqlalchemy.orm import Session
from app.services.workspace_service import WorkspaceService

class ProjectService:
    """Service class executing workspace registrations, file crawl scans, and statistics logs."""
    def __init__(self, db: Session):
        self.db = db
        self.workspace_service = WorkspaceService(db)

    def register_new_project(self, path: str):
        return self.workspace_service.register_workspace(path)

    def run_project_scan(self, project_id: str):
        return self.workspace_service.refresh_project(project_id)

    def get_project_statistics(self, project_id: str):
        return self.workspace_service.get_workspace_statistics(project_id)
