from fastapi import APIRouter, Depends, Body, HTTPException
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.database.schemas.project import ProjectResponse, ProjectScanRequest
from app.database.schemas.file import FileResponse
from app.services.workspace_service import WorkspaceService
from app.database.repositories.project_repository import ProjectRepository
from app.database.repositories.file_repository import FileRepository
from app.core.exceptions import ProjectNotFoundException
from typing import List

router = APIRouter(prefix="/projects", tags=["Projects"])

@router.get("", response_model=List[ProjectResponse])
def list_projects(db: Session = Depends(get_db)):
    """Lists all registered engineering projects in the database."""
    repo = ProjectRepository(db)
    projects = repo.list_all()
    return projects

@router.post("/scan")
def scan_project(
    payload: ProjectScanRequest,
    db: Session = Depends(get_db)
):
    """Triggers an incremental scan on a target workspace folder path."""
    service = WorkspaceService(db)
    # Automatically registers if not registered
    project = service.register_workspace(payload.path)
    result = service.refresh_project(project.id)
    return {
        "success": True,
        "message": "Scan completed successfully.",
        "data": result
    }

@router.get("/{project_id}/details", response_model=ProjectResponse)
def get_project_details(project_id: str, db: Session = Depends(get_db)):
    """Retrieves metadata details for a registered project."""
    repo = ProjectRepository(db)
    project = repo.get_by_id(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found.")
    return project

@router.get("/{project_id}/files", response_model=List[FileResponse])
def list_project_files(project_id: str, db: Session = Depends(get_db)):
    """Lists all indexed files for a project."""
    repo = FileRepository(db)
    files = repo.list_by_project(project_id)
    return files

@router.get("/{project_id}/structure")
def get_project_structure(project_id: str, db: Session = Depends(get_db)):
    """Compiles folder tree, modules tree, and dependencies list for a project."""
    service = WorkspaceService(db)
    structure = service.retrieve_project_structure(project_id)
    return structure
