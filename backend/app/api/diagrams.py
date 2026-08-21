from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.tools.project.diagram_generator import diagram_generator
from app.database.repositories.project_repository import ProjectRepository
from app.core.exceptions import PEISException

router = APIRouter(prefix="/diagrams", tags=["Diagram Generation"])

def _generate_or_handle_error(generator_func, db: Session, project_id: str, force_refresh: bool = False):
    repo = ProjectRepository(db)
    project = repo.get_by_id(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not registered.")
    
    try:
        markup = generator_func(db, project_id, force_refresh=force_refresh)
        return {"mermaid_code": markup, "error": False}
    except PEISException as e:
        msg = str(e.message)
        if "NO_API_KEY" in msg:
            code = "NO_API_KEY"
        elif "RATE_LIMITED" in msg:
            code = "RATE_LIMITED"
        elif "INVALID_KEY" in msg:
            code = "INVALID_KEY"
        else:
            code = "GENERATION_FAILED"
        return {"error": True, "code": code, "detail": msg, "status_code": e.status_code}
    except Exception as e:
        return {"error": True, "code": "GENERATION_FAILED", "detail": str(e), "status_code": 500}

@router.get("/er/{project_id}")
def get_er_diagram(project_id: str, force_refresh: bool = False, db: Session = Depends(get_db)):
    """Generates a Mermaid.js Entity-Relationship diagram markup representing project schemas."""
    return _generate_or_handle_error(diagram_generator.generate_er_diagram, db, project_id, force_refresh=force_refresh)

@router.get("/api-flow/{project_id}")
def get_api_flow_diagram(project_id: str, force_refresh: bool = False, db: Session = Depends(get_db)):
    """Generates a Mermaid.js flowchart diagram mapping API endpoint routes."""
    return _generate_or_handle_error(diagram_generator.generate_api_flow, db, project_id, force_refresh=force_refresh)

@router.get("/sequence/{project_id}")
def get_sequence_diagram(project_id: str, force_refresh: bool = False, db: Session = Depends(get_db)):
    """Generates a Mermaid.js sequence diagram mapping request-response lifecycles."""
    return _generate_or_handle_error(diagram_generator.generate_sequence_diagram, db, project_id, force_refresh=force_refresh)

@router.delete("/cache/{project_id}")
def clear_diagram_cache(project_id: str):
    """Flushes the in-memory diagram cache for a specific project workspace."""
    diagram_generator.clear_cache(project_id)
    return {"success": True, "message": f"Diagram cache cleared for project: {project_id}"}
