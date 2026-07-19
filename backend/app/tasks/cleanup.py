from app.database.session import SessionLocal
from app.database.models.cache import SystemCache
from app.utils.helpers import get_utc_now
from app.core.logging import logger

def run_cache_cleanup():
    """Identifies and purges expired key-value cache lines from the SQLite system cache."""
    logger.info("[Task:Cleanup] Running system cache garbage collector...")
    db = SessionLocal()
    try:
        now = get_utc_now()
        deleted = db.query(SystemCache).filter(SystemCache.expires_at < now).delete()
        db.commit()
        logger.info(f"[Task:Cleanup] Garbage collector completed. Purged {deleted} cache entries.")
    except Exception as e:
        logger.error(f"[Task:Cleanup] Garbage collector failed: {e}")
    finally:
        db.close()
