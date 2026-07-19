from sqlalchemy.orm import Session
from app.services.search_service import SearchService

class RAGService:
    """Service class executing retrieval-augmented search query operations."""
    def __init__(self, db: Session):
        self.db = db
        self.search_service = SearchService(db)

    def retrieve_context(self, project_id: str, query: str, limit: int = 5):
        return self.search_service.hybrid_search(project_id, query, limit=limit)
