from app.indexing.incremental_indexer import run_incremental_index
from app.core.logging import logger

class WorkspaceAgent:
    def __init__(self):
        self.name = "WorkspaceAgent"

    def scan_workspace(self, context: dict) -> dict:
        """Triggers the directory scanner and updates SQLite metadata and file hashes."""
        project_path = context["project_path"]
        db = context["db"]
        
        logger.info(f"[WorkspaceAgent] Starting incremental workspace scan for: {project_path}")
        result = run_incremental_index(db, project_path)
        logger.info(f"[WorkspaceAgent] Scan complete. Results: {result}")
        return result
