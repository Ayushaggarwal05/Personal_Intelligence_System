import os
from app.database.session import SessionLocal
from app.services.workspace_service import WorkspaceService
from app.indexing.watcher import workspace_watcher
from app.core.logging import logger

def trigger_background_workspace_refresh(project_path: str):
    """Callback function executing database incremental updates on modified directory triggers."""
    project_path = os.path.abspath(project_path)
    logger.info(f"[BackgroundIndexer] Executing asynchronous indexer refresh for: {project_path}")
    
    db = SessionLocal()
    try:
        service = WorkspaceService(db)
        project = service.project_repo.get_by_path(project_path)
        if not project:
            logger.warning(f"[BackgroundIndexer] Path '{project_path}' is not registered. Skipping refresh.")
            return
            
        results = service.refresh_project(project.id)
        logger.info(f"[BackgroundIndexer] Asynchronous refresh completed. Crawled metrics: {results}")
    except Exception as e:
        logger.error(f"[BackgroundIndexer] Asynchronous refresh failed: {e}")
    finally:
        db.close()

def initialize_watcher_triggers():
    """Binds indexer execution callbacks to background watchers and starts the monitoring threads."""
    logger.info("[BackgroundIndexer] Initializing background watcher triggers...")
    workspace_watcher.set_callback(trigger_background_workspace_refresh)
    workspace_watcher.start()
    logger.info("[BackgroundIndexer] Watcher triggers bound and monitoring loops started.")

def stop_watcher_triggers():
    """Shuts down background workspace watcher threads."""
    logger.info("[BackgroundIndexer] Stopping background watcher triggers...")
    workspace_watcher.stop()
