from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.services.search_service import SearchService
from typing import Optional, List

router = APIRouter(prefix="/search", tags=["Hybrid Search"])

@router.get("")
def search_project(
    project_id: str,
    query: str,
    type: Optional[str] = Query(None, description="Filter: file, symbol, route, function, class"),
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """Executes keyword-semantic hybrid searches over workspace codes and document text segments."""
    service = SearchService(db)
    results = service.hybrid_search(
        project_id=project_id,
        query=query,
        search_type=type,
        limit=limit
    )
    return {"results": results}

@router.get("/suggestions")
def search_suggestions(
    project_id: str,
    prefix: str,
    limit: int = 5,
    db: Session = Depends(get_db)
):
    """Generates autocomplete suggestions for matching symbol names or file paths."""
    service = SearchService(db)
    suggestions = service.get_search_suggestions(project_id, prefix, limit=limit)
    return {"suggestions": suggestions}
