import os
from app.tools.filesystem.ignore_parser import load_gitignore_matcher

IGNORE_DIRS = {
    ".git", "node_modules", "__pycache__", "venv", ".venv",
    ".next", "dist", "build", "target", ".idea", ".vscode", "storage"
}

IGNORE_EXTENSIONS = {
    ".jpg", ".jpeg", ".png", ".gif", ".svg", ".ico", ".webp",
    ".mp3", ".wav", ".mp4", ".mov",
    ".zip", ".tar", ".gz", ".rar", ".7z",
    ".db", ".sqlite", ".sqlite3",
    ".pyc", ".pyd", ".pyo",
    ".exe", ".bin", ".dll", ".so", ".dylib"
}

def list_workspace_files(workspace_path: str, custom_rules: list = None) -> list[str]:
    """Recursively lists files under workspace_path, filtering by default patterns and .gitignore rules."""
    file_list = []
    workspace_path = os.path.abspath(workspace_path)
    
    if not os.path.exists(workspace_path):
        return []

    # Initialize .gitignore matcher
    matcher = load_gitignore_matcher(workspace_path, custom_rules)

    for root, dirs, files in os.walk(workspace_path):
        # 1. Exclude ignored directories from recursion in-place
        dirs[:] = [
            d for d in dirs 
            if d not in IGNORE_DIRS and not matcher.should_ignore(os.path.join(root, d))
        ]
        
        for file in files:
            _, ext = os.path.splitext(file)
            if ext.lower() in IGNORE_EXTENSIONS:
                continue
            
            full_path = os.path.join(root, file)
            # 2. Check if .gitignore matcher ignores this file
            if matcher.should_ignore(full_path):
                continue
                
            file_list.append(full_path)
            
    return file_list
