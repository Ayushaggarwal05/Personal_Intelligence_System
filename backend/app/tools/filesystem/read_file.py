import os
from app.core.security import is_safe_path
from app.core.exceptions import FileNotFoundException

def read_workspace_file_content(base_dir: str, rel_file_path: str) -> str:
    """Reads the contents of a file safely, preventing directory traversal injection attacks."""
    full_path = os.path.join(base_dir, rel_file_path)
    if not is_safe_path(base_dir, full_path):
        raise PermissionError(f"Access denied. Path '{rel_file_path}' traverses out of boundary.")
        
    if not os.path.exists(full_path):
        raise FileNotFoundException(full_path)
        
    with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()
