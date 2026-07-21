from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from app.database.repositories.file_repository import FileRepository
from app.database.repositories.symbol_repository import SymbolRepository
from app.services.embedding_service import embedding_service
from app.memory.vector_store import vector_store

class SearchService:
    """Business layer orchestrating hybrid keyword-semantic search and suggestions filters."""
    def __init__(self, db: Session):
        self.db = db
        self.file_repo = FileRepository(db)
        self.symbol_repo = SymbolRepository(db)

    def hybrid_search(
        self, 
        project_id: str, 
        query: str, 
        search_type: Optional[str] = None, 
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Merges keyword symbol searches and semantic chunk matches into ranked outputs."""
        results = []

        # 1. Relational Database Keyword Match (SQLite)
        if search_type in {None, "file", "symbol", "route", "class", "function"}:
            symbols = self.symbol_repo.search_in_project(project_id, query, limit=limit)
            for s in symbols:
                if search_type and s.type != search_type and not (search_type == "symbol" and s.type in {"class", "function"}):
                    continue
                results.append({
                    "id": s.id,
                    "title": s.name,
                    "type": s.type,
                    "snippet": s.signature or "",
                    "score": 0.9, # default keyword score rank
                    "source": "relational"
                })

            # File path matching
            files = self.file_repo.search_by_keyword(project_id, query, limit=limit)
            for f in files:
                if not any(r["title"] == f.relative_path for r in results):
                    results.append({
                        "id": f.id,
                        "title": f.relative_path,
                        "type": "file",
                        "snippet": f"File path: {f.relative_path}",
                        "score": 0.85,
                        "source": "relational"
                    })

        # 2. Semantic Search Match (Vector Store)
        if search_type in {None, "chunks", "documentation"}:
            try:
                query_vector = embedding_service.get_embedding(query)
                semantic_hits = vector_store.search(
                    query_vector=query_vector,
                    project_id=project_id,
                    limit=limit
                )
                for hit in semantic_hits:
                    # hit contains "content", "file_id", "score", etc.
                    results.append({
                        "id": hit.get("id", ""),
                        "title": "Text Segment Match",
                        "type": "chunk",
                        "snippet": hit.get("content", "")[:200],
                        "score": hit.get("score", 0.7),
                        "source": "semantic"
                    })
            except Exception:
                pass

        # Sort combined results by keyword match in title, then score rank descending
        results.sort(key=lambda x: (1 if query.lower() in x["title"].lower() else 0, x["score"]), reverse=True)
        return results[:limit]

    def get_search_suggestions(self, project_id: str, prefix: str, limit: int = 5) -> List[str]:
        """Provides autocomplete list of matching symbol names or filenames."""
        suggestions = []
        symbols = self.symbol_repo.search_in_project(project_id, prefix, limit=limit)
        for s in symbols:
            if s.name not in suggestions:
                suggestions.append(s.name)
        
        files = self.file_repo.search_by_keyword(project_id, prefix, limit=limit)
        for f in files:
            name = f.relative_path.split("/")[-1]
            if name not in suggestions:
                suggestions.append(name)
                
        return suggestions[:limit]
