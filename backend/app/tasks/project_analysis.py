from app.database.session import SessionLocal
from app.services.workspace_service import WorkspaceService
from app.core.logging import logger

def run_async_project_profiler(project_path: str):
    """Profiles project workspace structure and frameworks configurations asynchronously."""
    logger.info(f"[Task:Analysis] Profiling workspace frameworks configuration at: {project_path}")
    db = SessionLocal()
    try:
        service = WorkspaceService(db)
        project = service.register_workspace(project_path)
        logger.info(f"[Task:Analysis] Profiling complete. Registered Project ID: {project.id}")
    except Exception as e:
        logger.error(f"[Task:Analysis] Profiling failed: {e}")
    finally:
        db.close()
