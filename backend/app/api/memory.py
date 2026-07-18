from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.services.memory_service import MemoryService
from app.core.exceptions import PEISException

router = APIRouter(prefix="/memory", tags=["Conversational Memory"])

@router.get("/history/{project_id}")
def get_chat_history(
    project_id: str,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """Retrieves conversation message logs mapped to a project workspace."""
    try:
        service = MemoryService(db)
        history = service.list_history(project_id, limit=limit)
        return {"history": history}
    except PEISException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)

@router.delete("/history/{project_id}")
def clear_chat_history(
    project_id: str,
    db: Session = Depends(get_db)
):
    """Deletes conversation message logs associated with a project."""
    try:
        service = MemoryService(db)
        service.clear_history(project_id)
        return {"success": True, "message": "History cleared successfully."}
    except PEISException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)

@router.get("/weak-areas/{project_id}")
def get_user_weak_areas(
    project_id: str,
    db: Session = Depends(get_db)
):
    """Identifies frequently missing vocabulary keywords across previous mock interviews."""
    try:
        service = MemoryService(db)
        weak_topics = service.get_weak_topics(project_id)
        return {"weak_topics": weak_topics}
    except PEISException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)

@router.get("/topics/{project_id}")
def get_frequently_discussed_topics(
    project_id: str,
    limit: int = 5,
    db: Session = Depends(get_db)
):
    """Extracts top keywords frequently typed by the developer in dialog logs."""
    try:
        service = MemoryService(db)
        topics = service.get_frequently_discussed_topics(project_id, limit=limit)
        return {"frequently_discussed_topics": topics}
    except PEISException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
