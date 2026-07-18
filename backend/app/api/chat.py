from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.orchestrator.workflow import WorkflowEngine
from app.core.exceptions import PEISException

router = APIRouter(prefix="/chat", tags=["Chat & Explanations"])

@router.post("/query")
def chat_query(
    project_id: str = Body(..., embed=True),
    message: str = Body(..., embed=True),
    db: Session = Depends(get_db)
):
    """Executes the explain/chat workflow pipeline to yield interview-focused response answers."""
    try:
        engine = WorkflowEngine(db)
        response = engine.run_explain_workflow(project_id, message)
        return {"response": response}
    except PEISException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/compare")
def compare_projects(
    project_id_a: str = Body(..., embed=True),
    project_id_b: str = Body(..., embed=True),
    db: Session = Depends(get_db)
):
    """Executes the comparative systems engineering workflow for two codebases."""
    try:
        engine = WorkflowEngine(db)
        comparison = engine.run_compare_workflow(project_id_a, project_id_b)
        return {"comparison": comparison}
    except PEISException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
