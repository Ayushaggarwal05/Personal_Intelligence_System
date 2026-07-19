from app.tools.project.structure_generator import structure_generator
from typing import Dict, Any

def detect_project_folders_tree(project_path: str) -> Dict[str, Any]:
    """Returns folders schema nested dictionaries representation."""
    return structure_generator.generate_folder_tree(project_path)
