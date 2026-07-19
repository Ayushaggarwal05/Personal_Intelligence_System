from sqlalchemy.orm import Session
from app.indexing.incremental_indexer import run_incremental_index

class IndexManager:
    """Manager class coordinating filesystem crawlers and incremental SQLite and LanceDB indexations."""
    def __init__(self, db: Session):
        self.db = db

    def scan_and_index_project(self, project_path: str) -> dict:
        """Executes full files crawl and updates files, symbols, and vector chunks caches."""
        return run_incremental_index(self.db, project_path)

# Expose helper initializer
def get_index_manager(db: Session) -> IndexManager:
    return IndexManager(db)
