from fastapi import APIRouter
from app.services.system_monitor import system_monitor

router = APIRouter(prefix="/system", tags=["System Status"])

@router.get("/diagnostics")
def get_system_diagnostics():
    """Gathers SQLite size parameters, watcher counts, OS architecture profile diagnostics."""
    diagnostics = system_monitor.get_system_diagnostics()
    return diagnostics
