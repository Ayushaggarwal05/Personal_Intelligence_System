from app.database.session import SessionLocal
from app.indexing.embedding_index import update_file_embeddings_index
from app.core.logging import logger

def run_async_embeddings_indexing(project_id: str, file_id: str, file_path: str):
    """Refreshes file semantic chunk vectors indices in LanceDB database."""
    logger.info(f"[Task:Embeddings] refreshing vectors for file: {file_path}")
    db = SessionLocal()
    try:
        update_file_embeddings_index(db, project_id, file_id, file_path)
        logger.info(f"[Task:Embeddings] Complete indexing for: {file_path}")
    except Exception as e:
        logger.error(f"[Task:Embeddings] Indexing failed: {e}")
    finally:
        db.close()
