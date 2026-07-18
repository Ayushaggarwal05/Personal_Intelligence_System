from fastapi import APIRouter, Depends, Body
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.database.schemas.project import ProjectResponse, ProjectScanRequest
from app.services.workspace_service import WorkspaceService
from app.indexing.watcher import workspace_watcher

router = APIRouter(prefix="/workspace", tags=["Workspace Management"])

@router.post("/register", response_model=ProjectResponse)
def register_workspace(
    payload: ProjectScanRequest,
    db: Session = Depends(get_db)
):
    """Registers a directory path, extracts frameworks and initializes watcher monitoring."""
    service = WorkspaceService(db)
    project = service.register_workspace(payload.path)
    return project

@router.delete("/remove/{project_id}")
def remove_workspace(
    project_id: str,
    db: Session = Depends(get_db)
):
    """Deletes workspace project mappings from SQLite databases."""
    service = WorkspaceService(db)
    success = service.remove_workspace(project_id)
    return {"success": success, "message": "Workspace removed successfully."}

@router.get("/status/{project_id}")
def get_workspace_watcher_status(
    project_id: str,
    db: Session = Depends(get_db)
):
    """Checks if a workspace path is actively registered under file change watchers."""
    service = WorkspaceService(db)
    project = service.project_repo.get_by_id(project_id)
    if not project:
        return {"project_id": project_id, "active": False, "message": "Project not registered."}
        
    is_active = project.path in workspace_watcher.watched_workspaces
    return {
        "project_id": project_id,
        "project_name": project.name,
        "path": project.path,
        "active": is_active
    }

@router.get("/statistics/{project_id}")
def get_workspace_statistics(
    project_id: str,
    db: Session = Depends(get_db)
):
    """Compiles total code files and token count metrics for a project."""
    service = WorkspaceService(db)
    stats = service.get_workspace_statistics(project_id)
    return stats
