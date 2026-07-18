import os
import sys
import platform
from app.core.settings import settings
from app.indexing.watcher import workspace_watcher
from app.core.logging import logger

class SystemMonitorService:
    """Diagnostics service compiling resource metrics, settings, and database states."""
    def __init__(self):
        pass

    def get_system_diagnostics(self) -> dict:
        """Collects database sizes, active models configurations, and OS profile metrics."""
        # 1. DB size check
        db_path = settings.DATABASE_URL.replace("sqlite:///", "")
        db_size_bytes = 0
        if os.path.exists(db_path):
            try:
                db_size_bytes = os.path.getsize(db_path)
            except Exception:
                pass

        # 2. Watcher statistics
        watched_paths = list(workspace_watcher.watched_workspaces.keys())

        # 3. OS info profiles (zero dependencies)
        sys_info = {
            "os": platform.system(),
            "os_release": platform.release(),
            "python_version": sys.version.split()[0],
            "machine": platform.machine()
        }

        # 4. Compile diagnostics payload
        return {
            "status": "online",
            "app_name": settings.PROJECT_NAME,
            "version": settings.VERSION,
            "active_llm_provider": settings.ACTIVE_LLM_PROVIDER,
            "active_model_name": settings.OLLAMA_MODEL,
            "database": {
                "engine": "SQLite",
                "path": db_path,
                "size_bytes": db_size_bytes,
                "status": "connected"
            },
            "workspace_watcher": {
                "active_watcher_count": len(watched_paths),
                "monitored_paths": watched_paths
            },
            "system": sys_info
        }

system_monitor = SystemMonitorService()
