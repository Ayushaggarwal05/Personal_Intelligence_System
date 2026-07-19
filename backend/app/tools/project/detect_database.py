from app.tools.project.detect_project import detect_project_profile

def detect_project_database_type(project_path: str) -> str:
    """Returns detected database engine keyword."""
    profile = detect_project_profile(project_path)
    return profile.get("database_type", "SQLite")
