from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.database.schemas.interview import (
    InterviewStartRequest,
    InterviewStartResponse,
    AnswerSubmitRequest,
    AnswerSubmitResponse
)
from app.database.models.project import Project
from app.orchestrator.workflow import WorkflowEngine
from app.core.exceptions import PEISException

router = APIRouter(prefix="/interview", tags=["Mock Interview"])

@router.post("/start", response_model=InterviewStartResponse)
def start_interview_session(
    payload: InterviewStartRequest,
    db: Session = Depends(get_db)
):
    """Starts a new mock interview session and generates the first question."""
    project = db.query(Project).filter(Project.path == payload.project_path).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not registered. Scan workspace first.")

    try:
        engine = WorkflowEngine(db)
        result = engine.run_interview_generate_workflow(project.id)
        return InterviewStartResponse(
            interview_id=result["interview_id"],
            qa_id=result["qa_id"],
            question=result["question"],
            type=result["type"],
            focus_area=result["focus_area"]
        )
    except PEISException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate question: {e}")


@router.post("/submit", response_model=AnswerSubmitResponse)
def submit_interview_answer(
    payload: AnswerSubmitRequest,
    db: Session = Depends(get_db)
):
    """Submits user response, grades it, logs score, and issues the next mock question."""
    project = db.query(Project).filter(Project.path == payload.project_path).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not registered.")

    try:
        engine = WorkflowEngine(db)
        
        # 1. Review and grade current answer
        evaluation = engine.run_interview_review_workflow(
            interview_id=payload.interview_id,
            qa_id=payload.qa_id,
            user_answer=payload.user_answer,
            project_id=project.id
        )
        
        # 2. Automatically generate the next question
        next_question = engine.run_interview_generate_workflow(project.id)
        
        return AnswerSubmitResponse(
            evaluation=evaluation,
            next_question=InterviewStartResponse(
                interview_id=next_question["interview_id"],
                qa_id=next_question["qa_id"],
                question=next_question["question"],
                type=next_question["type"],
                focus_area=next_question["focus_area"]
            )
        )
    except PEISException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
