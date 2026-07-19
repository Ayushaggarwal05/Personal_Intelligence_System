from app.database.session import SessionLocal
from app.tools.project.diagram_generator import diagram_generator
from app.database.models.diagram import Diagram
from app.core.logging import logger

def run_async_diagram_refresh(project_id: str, diagram_type: str):
    """Regenerates static architectural diagram markup and commits it to SQLite caches."""
    logger.info(f"[Task:Diagrams] Refreshing diagram type '{diagram_type}' for project: {project_id}")
    db = SessionLocal()
    try:
        # Generate diagram code
        if diagram_type == "er":
            code = diagram_generator.generate_er_diagram(db, project_id)
        elif diagram_type == "sequence":
            code = diagram_generator.generate_sequence_diagram(db, project_id)
        else:
            code = diagram_generator.generate_api_flow(db, project_id)
            
        # Write to SQLite
        diag = Diagram(
            id=f"{project_id}_{diagram_type}",
            project_id=project_id,
            type=diagram_type,
            mermaid_code=code
        )
        db.merge(diag)
        db.commit()
        logger.info(f"[Task:Diagrams] Complete diagram cache commit for '{diagram_type}'.")
    except Exception as e:
        logger.error(f"[Task:Diagrams] Refresh failed: {e}")
    finally:
        db.close()
