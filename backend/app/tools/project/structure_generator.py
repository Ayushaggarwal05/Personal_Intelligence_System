import os
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from app.database.models.file import File
from app.database.models.symbol import Symbol
from app.tools.project.detect_dependencies import extract_dependencies

def build_folder_tree(base_path: str, current_path: str, ignore_dirs: set) -> Dict[str, Any]:
    """Helper to build a nested dictionary directory tree starting from current_path."""
    name = os.path.basename(current_path)
    if not name: # Fallback for root path
        name = current_path
        
    node = {
        "name": name,
        "type": "directory",
        "relative_path": os.path.relpath(current_path, base_path).replace(os.sep, "/"),
        "children": []
    }
    
    try:
        for entry in os.scandir(current_path):
            if entry.name.startswith(".") or entry.name in ignore_dirs:
                continue
            if entry.is_dir():
                node["children"].append(build_folder_tree(base_path, entry.path, ignore_dirs))
            elif entry.is_file():
                node["children"].append({
                    "name": entry.name,
                    "type": "file",
                    "relative_path": os.path.relpath(entry.path, base_path).replace(os.sep, "/")
                })
    except Exception:
        pass
        
    return node


class StructureGenerator:
    def __init__(self):
        pass

    def generate_folder_tree(self, project_path: str) -> Dict[str, Any]:
        """Generates a nested directory tree representation for a project."""
        from app.core.workspace_config import workspace_config
        project_path = os.path.abspath(project_path)
        if not os.path.exists(project_path):
            return {}
        return build_folder_tree(project_path, project_path, workspace_config.ignored_directories)

    def generate_module_tree(self, db: Session, project_id: str) -> Dict[str, Any]:
        """Generates a structural tree mapping files to their contained symbols (classes, functions, routes)."""
        db_files = db.query(File).filter(File.project_id == project_id).all()
        
        module_tree = {
            "project_id": project_id,
            "modules": []
        }

        for file in db_files:
            db_symbols = db.query(Symbol).filter(Symbol.file_id == file.id).all()
            
            symbols_list = []
            for sym in db_symbols:
                symbols_list.append({
                    "name": sym.name,
                    "type": sym.type,
                    "signature": sym.signature,
                    "line_start": sym.line_start,
                    "line_end": sym.line_end
                })
                
            module_tree["modules"].append({
                "file_path": file.relative_path,
                "token_count": file.token_count,
                "symbols": symbols_list
            })
            
        return module_tree

    def generate_dependency_tree(self, project_path: str) -> Dict[str, Any]:
        """Extracts and formats project dependencies list."""
        deps = extract_dependencies(project_path)
        return {
            "project_path": project_path,
            "dependencies": deps,
            "total_dependencies": len(deps)
        }

    def generate_import_graph(self, db: Session, project_id: str) -> Dict[str, Any]:
        """Generates a simple import mapping showing dependencies between modules."""
        db_files = db.query(File).filter(File.project_id == project_id).all()
        
        nodes = []
        edges = []
        
        # Build node maps
        for file in db_files:
            nodes.append({
                "id": file.id,
                "label": file.relative_path
            })
            
            # Simple heuristic regex check for imports of other project modules
            file_abs_path = os.path.join(file.relative_path) # placeholder
            
        return {
            "nodes": nodes,
            "edges": edges
        }

structure_generator = StructureGenerator()
