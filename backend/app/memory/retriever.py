from sqlalchemy.orm import Session
from app.services.search_service import SearchService
from typing import List, Dict, Any

class ProjectKnowledgeRetriever:
    """Retriever class executing semantic and keyword hybrid lookup queries."""
    def __init__(self, db: Session):
        self.db = db
        self.search_service = SearchService(db)

    def retrieve_relevant_context(self, project_id: str, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Invokes hybrid search service to find matching documentation chunks or code symbols."""
        return self.search_service.hybrid_search(
            project_id=project_id,
            query=query,
            limit=limit
        )
