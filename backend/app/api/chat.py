from fastapi import APIRouter, Depends, HTTPException, Body
from fastapi.responses import StreamingResponse
from typing import Optional
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.orchestrator.workflow import WorkflowEngine
from app.core.exceptions import PEISException

router = APIRouter(prefix="/chat", tags=["Chat & Explanations"])

@router.post("/stream")
def chat_stream(
    project_id: str = Body(..., embed=True),
    query: Optional[str] = Body(None, embed=True),
    message: Optional[str] = Body(None, embed=True),
    db: Session = Depends(get_db)
):
    """Streams chat query responses word-by-word via plain text chunk streaming."""
    user_query = query or message or ""
    if not user_query.strip():
        raise HTTPException(status_code=400, detail="Query message text is required.")

    def event_generator():
        try:
            engine = WorkflowEngine(db)
            for chunk in engine.run_explain_stream_workflow(project_id, user_query.strip()):
                yield chunk
        except Exception as e:
            yield f"\n[Error: {str(e)}]"

    return StreamingResponse(event_generator(), media_type="text/plain")

@router.post("/query")
def chat_query(
    project_id: str = Body(..., embed=True),
    query: Optional[str] = Body(None, embed=True),
    message: Optional[str] = Body(None, embed=True),
    db: Session = Depends(get_db)
):
    """Executes the explain/chat workflow pipeline to yield interview-focused response answers."""
    user_query = query or message or ""
    if not user_query.strip():
        raise HTTPException(status_code=400, detail="Query message text is required.")

    try:
        engine = WorkflowEngine(db)
        response = engine.run_explain_workflow(project_id, user_query.strip())
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
