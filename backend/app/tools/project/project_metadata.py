from app.tools.project.detect_project import detect_project_profile
from typing import Dict, Any

def get_project_metadata_profile(project_path: str) -> Dict[str, Any]:
    """Compiles profile specifications of a project path."""
    return detect_project_profile(project_path)
