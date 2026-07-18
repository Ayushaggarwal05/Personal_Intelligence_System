from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.tools.project.diagram_generator import diagram_generator
from app.database.repositories.project_repository import ProjectRepository

router = APIRouter(prefix="/diagrams", tags=["Diagram Generation"])

@router.get("/er/{project_id}")
def get_er_diagram(project_id: str, db: Session = Depends(get_db)):
    """Generates a Mermaid.js Entity-Relationship diagram markup representing project schemas."""
    repo = ProjectRepository(db)
    project = repo.get_by_id(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not registered.")
    
    markup = diagram_generator.generate_er_diagram(db, project_id)
    return {"mermaid_code": markup}

@router.get("/api-flow/{project_id}")
def get_api_flow_diagram(project_id: str, db: Session = Depends(get_db)):
    """Generates a Mermaid.js flowchart diagram mapping API endpoint routes."""
    repo = ProjectRepository(db)
    project = repo.get_by_id(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not registered.")
        
    markup = diagram_generator.generate_api_flow(db, project_id)
    return {"mermaid_code": markup}

@router.get("/sequence/{project_id}")
def get_sequence_diagram(project_id: str, db: Session = Depends(get_db)):
    """Generates a Mermaid.js sequence diagram mapping request-response lifecycles."""
    repo = ProjectRepository(db)
    project = repo.get_by_id(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not registered.")
        
    markup = diagram_generator.generate_sequence_diagram(db, project_id)
    return {"mermaid_code": markup}
