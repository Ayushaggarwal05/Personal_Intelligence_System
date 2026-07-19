from sqlalchemy.orm import Session
from app.core.logging import logger
from app.database.models.symbol import Symbol
from app.tools.parsers.python_parser import parse_python_file
from app.tools.parsers.javascript_parser import parse_javascript_file
import os

def index_file_metadata_symbols(db: Session, file_id: str, file_path: str):
    """Parses code AST files and saves extracted class, function, and route symbols inside SQLite."""
    _, ext = os.path.splitext(file_path)
    ext = ext.lower()
    
    symbols = []
    try:
        if ext == ".py":
            symbols = parse_python_file(file_path)
        elif ext in {".js", ".ts", ".jsx", ".tsx"}:
            symbols = parse_javascript_file(file_path)
        elif ext == ".go":
            from app.tools.parsers.go_parser import parse_go_file
            symbols = parse_go_file(file_path)
        elif ext == ".java":
            from app.tools.parsers.java_parser import parse_java_file
            symbols = parse_java_file(file_path)
        elif ext in {".cpp", ".h", ".hpp", ".cc"}:
            from app.tools.parsers.cpp_parser import parse_cpp_file
            symbols = parse_cpp_file(file_path)
            
        # Write to SQLite
        for sym in symbols:
            db_sym = Symbol(
                id=f"{file_id}_{sym['name']}_{sym['line_start']}",
                file_id=file_id,
                name=sym["name"],
                type=sym["type"],
                signature=sym["signature"],
                docstring=sym["docstring"],
                line_start=sym["line_start"],
                line_end=sym["line_end"]
            )
            db.merge(db_sym)
            
        db.commit()
        logger.info(f"[MetadataIndex] Parsed and indexed {len(symbols)} symbols from: {file_path}")
    except Exception as e:
        logger.error(f"[MetadataIndex] Failed to index symbols for {file_path}: {e}")
