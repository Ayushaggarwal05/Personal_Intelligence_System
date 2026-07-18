import os
import time
import threading
from typing import Dict, Set, Callable, Optional
from app.core.logging import logger
from app.tools.filesystem.list_directory import list_workspace_files
from app.tools.filesystem.file_hash import calculate_file_hash

class WorkspaceWatcher:
    """Background filesystem monitor that tracks workspace modifications using polling and debouncing."""
    def __init__(self, debounce_seconds: float = 2.0, poll_interval: float = 3.0):
        self.debounce_seconds = debounce_seconds
        self.poll_interval = poll_interval
        
        # Maps project_path -> {file_path -> (hash, last_modified)}
        self.watched_workspaces: Dict[str, Dict[str, tuple]] = {}
        # Maps project_path -> last_change_time
        self.pending_updates: Dict[str, float] = {}
        # Callback trigger: Callable[[project_path], None]
        self.on_change_callback: Optional[Callable[[str], None]] = None
        
        self._lock = threading.Lock()
        self._stop_event = threading.Event()
        self._thread = None

    def register_workspace(self, project_path: str):
        """Adds a project workspace folder to the background monitor."""
        project_path = os.path.abspath(project_path)
        with self._lock:
            if project_path not in self.watched_workspaces:
                self.watched_workspaces[project_path] = self._snapshot_workspace(project_path)
                logger.info(f"[WorkspaceWatcher] Started monitoring workspace path: {project_path}")

    def unregister_workspace(self, project_path: str):
        """Removes a project folder from the background monitor."""
        project_path = os.path.abspath(project_path)
        with self._lock:
            if project_path in self.watched_workspaces:
                del self.watched_workspaces[project_path]
                if project_path in self.pending_updates:
                    del self.pending_updates[project_path]
                logger.info(f"[WorkspaceWatcher] Stopped monitoring workspace path: {project_path}")

    def set_callback(self, callback: Callable[[str], None]):
        """Sets the trigger function that is invoked when a workspace has modified files."""
        self.on_change_callback = callback

    def start(self):
        """Spins up the background watcher thread loop."""
        if self._thread is not None:
            return
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._watch_loop, daemon=True)
        self._thread.start()
        logger.info("[WorkspaceWatcher] Background watcher thread started.")

    def stop(self):
        """Stops the background thread."""
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=5)
            self._thread = None
        logger.info("[WorkspaceWatcher] Background watcher thread stopped.")

    def _snapshot_workspace(self, path: str) -> Dict[str, tuple]:
        """Takes a fast snapshot of files, sizes, and timestamps inside the workspace."""
        snapshot = {}
        files = list_workspace_files(path)
        for f in files:
            try:
                mtime = os.path.getmtime(f)
                size = os.path.getsize(f)
                snapshot[f] = (mtime, size)
            except Exception:
                continue
        return snapshot

    def _watch_loop(self):
        while not self._stop_event.is_set():
            time.sleep(self.poll_interval)
            
            with self._lock:
                current_time = time.time()
                
                # 1. Scan monitored workspaces for file changes
                for path, old_snapshot in list(self.watched_workspaces.items()):
                    current_snapshot = self._snapshot_workspace(path)
                    
                    # Detect structural differences: added, deleted, or altered sizes/timestamps
                    has_changes = False
                    if set(old_snapshot.keys()) != set(current_snapshot.keys()):
                        has_changes = True
                    else:
                        for f, old_val in old_snapshot.items():
                            if current_snapshot.get(f) != old_val:
                                has_changes = True
                                break
                    
                    if has_changes:
                        # Record/update modified timestamp
                        self.pending_updates[path] = current_time
                        # Update current snapshot reference
                        self.watched_workspaces[path] = current_snapshot
                        logger.info(f"[WorkspaceWatcher] Change detected in workspace: {path}")

                # 2. Process debouncing updates queue
                for path, change_time in list(self.pending_updates.items()):
                    if current_time - change_time >= self.debounce_seconds:
                        del self.pending_updates[path]
                        if self.on_change_callback:
                            logger.info(f"[WorkspaceWatcher] Debounce complete. Triggering indexer refresh for: {path}")
                            # Execute callback in a separate thread so it doesn't block the polling loop
                            threading.Thread(
                                target=self.on_change_callback, 
                                args=(path,), 
                                daemon=True
                            ).start()

workspace_watcher = WorkspaceWatcher()
