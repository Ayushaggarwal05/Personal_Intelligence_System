from typing import Set
from pydantic import BaseModel

class WorkspaceConfig(BaseModel):
    # Extensions that PEIS parser supports and indices
    allowed_extensions: Set[str] = {
        ".py", ".js", ".ts", ".jsx", ".tsx", ".go", 
        ".java", ".cpp", ".c", ".h", ".cs", 
        ".md", ".txt", ".json", ".yaml", ".yml", ".pdf"
    }
    
    # Folders that the recursive scanner ignores by default
    ignored_directories: Set[str] = {
        ".git", "node_modules", "__pycache__", "venv", ".venv",
        "env", ".env", "dist", "build", "out", "target", 
        ".idea", ".vscode", "storage", ".next", ".cache", "bin", "obj"
    }
    
    # Maximum file size allowed to be read or chunked (2 MB limit by default)
    max_file_size_bytes: int = 2 * 1024 * 1024
    
    # Text-to-token converter denominator (e.g., characters divided by 4)
    token_character_ratio: int = 4

workspace_config = WorkspaceConfig()
