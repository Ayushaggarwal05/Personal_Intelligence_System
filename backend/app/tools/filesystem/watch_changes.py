from app.indexing.watcher import workspace_watcher

def monitor_workspace_changes(project_path: str):
    """Registers project path inside the background changes watcher thread."""
    workspace_watcher.register_workspace(project_path)
