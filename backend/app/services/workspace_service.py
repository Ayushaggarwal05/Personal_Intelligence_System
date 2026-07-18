import os
import uuid
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from app.core.base_interfaces import BaseService
from app.core.logging import logger
from app.core.exceptions import ProjectNotFoundException, ValidationException
from app.database.models.project import Project
from app.database.models.file import File
from app.database.repositories.project_repository import ProjectRepository
from app.database.repositories.file_repository import FileRepository
from app.database.repositories.symbol_repository import SymbolRepository
from app.database.repositories.diagram_repository import DiagramRepository
from app.tools.project.detect_project import detect_project_profile
from app.tools.project.structure_generator import structure_generator
from app.indexing.incremental_indexer import run_incremental_index
from app.indexing.watcher import workspace_watcher

class WorkspaceService(BaseService):
    """Business logic service managing project workspaces registration, indexing, refresh and schema maps."""
    def __init__(self, db: Session):
        self.db = db
        self.project_repo = ProjectRepository(db)
        self.file_repo = FileRepository(db)
        self.symbol_repo = SymbolRepository(db)
        self.diagram_repo = DiagramRepository(db)

    def execute(self, *args, **kwargs):
        """Implements BaseService abstract interface."""
        pass

    def register_workspace(self, workspace_path: str) -> Project:
        """Registers a project path in SQLite database and schedules background file monitoring."""
        workspace_path = os.path.abspath(workspace_path)
        if not os.path.exists(workspace_path):
            raise ValidationException(f"Path '{workspace_path}' does not exist on disk.")

        # 1. Detect project type and frameworks
        logger.info(f"Profiling project codebase framework at: {workspace_path}")
        profile = detect_project_profile(workspace_path)

        # 2. Check if already registered
        existing_proj = self.project_repo.get_by_path(workspace_path)
        if existing_proj:
            # Update details and return
            existing_proj.framework = profile["framework"]
            existing_proj.database_type = profile["database_type"]
            self.db.commit()
            
            # Start background monitoring
            workspace_watcher.register_workspace(workspace_path)
            return existing_proj

        # 3. Create new project record
        project_id = str(uuid.uuid4())
        project_name = os.path.basename(workspace_path) or "PEIS Workspace"
        
        project = Project(
            id=project_id,
            name=project_name,
            path=workspace_path,
            framework=profile["framework"],
            database_type=profile["database_type"],
            summary=f"Primary language: {profile['project_type']}. Frameworks: {', '.join(profile['frameworks'])}."
        )
        
        registered = self.project_repo.create(project)
        logger.info(f"Registered new workspace project: {project_name} [ID: {project_id}]")
        
        # Start background monitoring
        workspace_watcher.register_workspace(workspace_path)
        return registered

    def remove_workspace(self, project_id: str) -> bool:
        """Removes project database mappings and stops background watcher monitoring."""
        project = self.project_repo.get_by_id(project_id)
        if not project:
            raise ProjectNotFoundException(project_id)
            
        workspace_path = project.path
        
        # Stop background watcher
        workspace_watcher.unregister_workspace(workspace_path)
        
        # Deleting project cascades SQLite records (files, symbols, interviews)
        logger.info(f"Deleting project workspace record: {project.name} (Path: {workspace_path})")
        return self.project_repo.delete(project_id)

    def refresh_project(self, project_id: str) -> dict:
        """Forces an incremental scan to reload files and symbols mappings."""
        project = self.project_repo.get_by_id(project_id)
        if not project:
            raise ProjectNotFoundException(project_id)
            
        logger.info(f"Triggering refresh index scan for: {project.name}")
        results = run_incremental_index(self.db, project.path)
        return results

    def get_workspace_statistics(self, project_id: str) -> dict:
        """Compiles total code files and token count metrics for a project."""
        project = self.project_repo.get_by_id(project_id)
        if not project:
            raise ProjectNotFoundException(project_id)

        files = self.file_repo.list_by_project(project_id)
        total_files = len(files)
        total_tokens = sum(f.token_count for f in files)
        
        # Count by category
        code_files = sum(1 for f in files if not f.relative_path.endswith((".md", ".txt", ".pdf")))
        doc_files = total_files - code_files
        
        return {
            "project_name": project.name,
            "total_files": total_files,
            "total_tokens": total_tokens,
            "code_files": code_files,
            "doc_files": doc_files
        }

    def retrieve_project_structure(self, project_id: str) -> dict:
        """Compiles folder tree, modules tree, and dependencies list for a project."""
        project = self.project_repo.get_by_id(project_id)
        if not project:
            raise ProjectNotFoundException(project_id)

        folder_tree = structure_generator.generate_folder_tree(project.path)
        module_tree = structure_generator.generate_module_tree(self.db, project_id)
        deps_data = structure_generator.generate_dependency_tree(project.path)

        return {
            "folder_tree": folder_tree,
            "module_tree": module_tree,
            "dependencies": deps_data["dependencies"]
        }
