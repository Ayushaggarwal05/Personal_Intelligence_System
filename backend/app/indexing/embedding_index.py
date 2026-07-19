from sqlalchemy.orm import Session
from app.core.logging import logger
from app.tools.project.chunker import chunk_file_for_indexing
from app.memory.vector_store import vector_store

def update_file_embeddings_index(db: Session, project_id: str, file_id: str, file_path: str):
    """Chunks file text/code and indexes segments inside the vector store database."""
    logger.info(f"[EmbeddingIndex] Generating text chunks for file ID: {file_id}")
    chunks = chunk_file_for_indexing(file_path, project_id, file_id)
    if chunks:
        # Add to vector store
        vector_store.add_documents(chunks)
        logger.info(f"[EmbeddingIndex] Successfully indexed {len(chunks)} text chunks in LanceDB.")
