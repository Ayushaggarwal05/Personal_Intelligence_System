from app.tools.project.detect_project import detect_project_profile
from typing import Optional

def detect_project_primary_framework(project_path: str) -> Optional[str]:
    """Returns detected web framework name."""
    profile = detect_project_profile(project_path)
    return profile.get("framework")
