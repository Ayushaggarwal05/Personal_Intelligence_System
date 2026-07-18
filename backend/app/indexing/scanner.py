import os
import uuid
from sqlalchemy.orm import Session
from app.database.models.project import Project
from app.database.models.file import File
from app.tools.filesystem.list_directory import list_workspace_files
from app.tools.filesystem.file_hash import calculate_file_hash
from app.core.logging import logger

def scan_project_workspace(db: Session, project_path: str) -> dict:
    """Scans the project workspace and returns new, modified, and deleted files compared to SQLite."""
    project_path = os.path.abspath(project_path)
    
    # 1. Fetch or create project in DB
    project = db.query(Project).filter(Project.path == project_path).first()
    if not project:
        project_id = str(uuid.uuid4())
        project_name = os.path.basename(project_path) or "Unnamed Project"
        project = Project(id=project_id, name=project_name, path=project_path)
        db.add(project)
        db.commit()
        logger.info(f"Registered new project '{project_name}' under {project_path}")
    else:
        logger.info(f"Scanning existing project '{project.name}' at {project_path}")

    # 2. Get all file records from SQLite for this project
    db_files = db.query(File).filter(File.project_id == project.id).all()
    db_file_map = {os.path.join(project_path, f.relative_path): f for f in db_files}

    # 3. Get all files currently on disk
    disk_files = list_workspace_files(project_path)
    disk_file_set = set(disk_files)

    new_files = []
    modified_files = []
    deleted_files = []

    # 4. Compare disk files against database map
    for disk_path in disk_files:
        rel_path = os.path.relpath(disk_path, project_path)
        last_mod = int(os.path.getmtime(disk_path))
        
        if disk_path not in db_file_map:
            # File is new
            new_files.append({
                "absolute_path": disk_path,
                "relative_path": rel_path,
                "last_modified": last_mod
            })
        else:
            # File exists, check if modified (compare timestamps or hashes)
            db_file_record = db_file_map[disk_path]
            if db_file_record.last_modified != last_mod:
                # If modified time is different, calculate hash to check content changes
                current_hash = calculate_file_hash(disk_path)
                if db_file_record.file_hash != current_hash:
                    modified_files.append({
                        "absolute_path": disk_path,
                        "relative_path": rel_path,
                        "last_modified": last_mod,
                        "current_hash": current_hash,
                        "db_file_record": db_file_record
                    })

    # 5. Check for deleted files (exist in database but not on disk)
    for db_path, db_file_record in db_file_map.items():
        if db_path not in disk_file_set:
            deleted_files.append(db_file_record)

    logger.info(
        f"Scan results for '{project.name}': "
        f"{len(new_files)} new files, {len(modified_files)} modified files, {len(deleted_files)} deleted files."
    )

    return {
        "project": project,
        "new": new_files,
        "modified": modified_files,
        "deleted": deleted_files
    }
