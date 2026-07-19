from app.database.session import SessionLocal
from app.services.workspace_service import WorkspaceService
from app.core.logging import logger

def run_async_workspace_scan(project_id: str):
    """Executes files scanning task asynchronously in background thread."""
    logger.info(f"[Task:Scan] Starting workspace scan for project ID: {project_id}")
    db = SessionLocal()
    try:
        service = WorkspaceService(db)
        results = service.refresh_project(project_id)
        logger.info(f"[Task:Scan] Workspace scan completed. Details: {results}")
    except Exception as e:
        logger.error(f"[Task:Scan] Failed to execute scan: {e}")
    finally:
        db.close()
