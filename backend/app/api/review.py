from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.database.schemas.interview import AnswerSubmitRequest
from app.orchestrator.workflow import WorkflowEngine
from app.database.models.project import Project
from app.core.exceptions import PEISException

router = APIRouter(prefix="/review", tags=["Mock Interview Review"])

@router.post("/answer")
def review_single_answer(
    payload: AnswerSubmitRequest,
    db: Session = Depends(get_db)
):
    """Reviews and grades a single mock interview response answer directly."""
    project = db.query(Project).filter(Project.path == payload.project_path).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not registered.")

    try:
        engine = WorkflowEngine(db)
        evaluation = engine.run_interview_review_workflow(
            interview_id=payload.interview_id,
            qa_id=payload.qa_id,
            user_answer=payload.user_answer,
            project_id=project.id
        )
        return {"evaluation": evaluation}
    except PEISException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
