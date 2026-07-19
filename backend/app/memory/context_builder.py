from sqlalchemy.orm import Session
from app.database.models.symbol import Symbol
from app.database.models.file import File

def build_project_symbols_summary(db: Session, project_id: str, limit: int = 15) -> str:
    """Builds a technical text context summary of project AST symbols."""
    symbols = db.query(Symbol).join(File).filter(
        File.project_id == project_id
    ).limit(limit).all()
    
    if not symbols:
        return "No code structures indexed."
        
    lines = []
    for s in symbols:
        lines.append(f"- [{s.type.upper()}] Name: {s.name} | Signature: {s.signature or ''}")
    return "\n".join(lines)
