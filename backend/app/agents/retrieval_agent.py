from sqlalchemy.orm import Session
from app.database.models.project import Project
from app.database.models.file import File
from app.database.models.symbol import Symbol
from app.services.embedding_service import embedding_service
from app.memory.vector_store import vector_store
from app.tools.filesystem.search_files import search_files_by_keyword
from app.core.logging import logger
import os

class RetrievalAgent:
    def __init__(self):
        self.name = "RetrievalAgent"

    def retrieve_context(self, context: dict) -> dict:
        """Helper action mapped to standard chat flow context retrieval."""
        return self.hybrid_search(context)

    def hybrid_search(self, context: dict) -> dict:
        """Merges semantic search vectors and keyword lookups into a ranked results list."""
        query = context["query"]
        project_path = context["project_path"]
        db: Session = context["db"]

        project = db.query(Project).filter(Project.path == project_path).first()
        if not project:
            logger.warning(f"Project not found for path {project_path}. Running default search.")
            return {"results": []}

        # 1. Semantic Search
        logger.info(f"[RetrievalAgent] Running semantic search for query: '{query}'")
        query_vec = embedding_service.get_embedding(query)
        semantic_results = vector_store.search(query_vector=query_vec, project_id=project.id, limit=5)

        # 2. Keyword Symbol Search in SQLite (match function names, route names, classes)
        logger.info(f"[RetrievalAgent] Running relational database keyword search...")
        db_symbols = db.query(Symbol).join(File).filter(
            File.project_id == project.id,
            Symbol.name.like(f"%{query}%") | Symbol.signature.like(f"%{query}%")
        ).limit(5).all()

        keyword_results = []
        for sym in db_symbols:
            keyword_results.append({
                "type": "symbol",
                "name": sym.name,
                "symbol_type": sym.type,
                "signature": sym.signature,
                "line_start": sym.line_start
            })

        # Assemble and structure output
        logger.info(f"[RetrievalAgent] Search finished. Found {len(semantic_results)} semantic and {len(keyword_results)} keyword symbols.")
        return {
            "semantic_matches": semantic_results,
            "keyword_symbols": keyword_results
        }
