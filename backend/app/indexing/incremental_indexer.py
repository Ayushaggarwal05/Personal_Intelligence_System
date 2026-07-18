import os
import uuid
from sqlalchemy.orm import Session
from app.indexing.scanner import scan_project_workspace
from app.database.models.file import File
from app.database.models.symbol import Symbol
from app.tools.filesystem.file_hash import calculate_file_hash
from app.tools.parsers.python_parser import parse_python_file
from app.tools.parsers.javascript_parser import parse_javascript_file
from app.core.logging import logger

def estimate_tokens(file_path: str) -> int:
    """Estimates the token count of a text file using character-based approximation."""
    try:
        if not os.path.exists(file_path):
            return 0
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        return len(content) // 4
    except Exception:
        return 0

def extract_and_store_symbols(db: Session, file_id: str, abs_path: str):
    """Parses symbols from a file and inserts them into the symbols database."""
    _, ext = os.path.splitext(abs_path)
    ext = ext.lower()
    
    symbols_data = []
    if ext == ".py":
        symbols_data = parse_python_file(abs_path)
    elif ext in {".js", ".ts", ".jsx", ".tsx"}:
        symbols_data = parse_javascript_file(abs_path)

    for sym in symbols_data:
        sym_record = Symbol(
            id=str(uuid.uuid4()),
            file_id=file_id,
            name=sym["name"],
            type=sym["type"],
            signature=sym["signature"],
            docstring=sym["docstring"],
            line_start=sym["line_start"],
            line_end=sym["line_end"]
        )
        db.add(sym_record)
        
    if symbols_data:
        logger.info(f"Parsed {len(symbols_data)} symbols from {os.path.basename(abs_path)}")

def run_incremental_index(db: Session, project_path: str) -> dict:
    """Runs scanning and performs database updates for new, modified, and deleted files."""
    scan_results = scan_project_workspace(db, project_path)
    
    project = scan_results["project"]
    new_files = scan_results["new"]
    modified_files = scan_results["modified"]
    deleted_files = scan_results["deleted"]

    # 1. Process Deleted Files
    for db_file in deleted_files:
        logger.info(f"Removing deleted file record: {db_file.relative_path}")
        db.delete(db_file)
    db.commit()

    # 2. Process New Files
    for new_file in new_files:
        abs_path = new_file["absolute_path"]
        rel_path = new_file["relative_path"]
        last_mod = new_file["last_modified"]
        
        try:
            file_hash = calculate_file_hash(abs_path)
            tokens = estimate_tokens(abs_path)
            file_id = str(uuid.uuid4())
            
            file_record = File(
                id=file_id,
                project_id=project.id,
                relative_path=rel_path,
                file_hash=file_hash,
                last_modified=last_mod,
                token_count=tokens
            )
            db.add(file_record)
            
            # Extract and store symbols
            extract_and_store_symbols(db, file_id, abs_path)
            logger.info(f"Indexed new file: {rel_path} ({tokens} est. tokens)")
        except Exception as e:
            logger.error(f"Failed to index new file {rel_path}: {e}")
            
    db.commit()

    # 3. Process Modified Files
    for mod_file in modified_files:
        rel_path = mod_file["relative_path"]
        last_mod = mod_file["last_modified"]
        file_hash = mod_file["current_hash"]
        db_file = mod_file["db_file_record"]
        abs_path = mod_file["absolute_path"]
        
        try:
            tokens = estimate_tokens(abs_path)
            
            db_file.file_hash = file_hash
            db_file.last_modified = last_mod
            db_file.token_count = tokens
            
            # Remove existing symbols for this modified file first
            db.query(Symbol).filter(Symbol.file_id == db_file.id).delete()
            
            # Extract and store updated symbols
            extract_and_store_symbols(db, db_file.id, abs_path)
            logger.info(f"Updated modified file: {rel_path} ({tokens} est. tokens)")
        except Exception as e:
            logger.error(f"Failed to update modified file {rel_path}: {e}")
            
    db.commit()

    return {
        "project_id": project.id,
        "project_name": project.name,
        "new_count": len(new_files),
        "modified_count": len(modified_files),
        "deleted_count": len(deleted_files)
    }
