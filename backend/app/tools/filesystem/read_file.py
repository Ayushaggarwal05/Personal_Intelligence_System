import os
from app.core.security import is_safe_path
from app.core.exceptions import FileNotFoundException

def is_binary_file(file_path: str) -> bool:
    """Robustly checks if a file is binary by looking for null bytes in the first 1024 bytes."""
    if not os.path.exists(file_path) or os.path.isdir(file_path):
        return False
    try:
        with open(file_path, "rb") as f:
            chunk = f.read(1024)
            if b"\x00" in chunk:
                return True
    except Exception:
        pass
    return False

def read_workspace_file_content(base_dir: str, rel_file_path: str) -> str:
    """Reads the contents of a file safely, preventing directory traversal and binary file corruption."""
    full_path = os.path.join(base_dir, rel_file_path)
    if not is_safe_path(base_dir, full_path):
        raise PermissionError(f"Access denied. Path '{rel_file_path}' traverses out of boundary.")
        
    if not os.path.exists(full_path):
        raise FileNotFoundException(full_path)
        
    if is_binary_file(full_path):
        raise ValueError(f"Failed to read file: '{rel_file_path}' is a binary file and cannot be read as text.")
        
    with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()
