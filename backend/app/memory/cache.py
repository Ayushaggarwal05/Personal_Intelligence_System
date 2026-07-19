from sqlalchemy.orm import Session
from app.database.models.cache import SystemCache
from app.utils.helpers import get_utc_now
import json
from typing import Optional, Any

class SystemCacheManager:
    """Helper manager saving and fetching cached execution queries using SQLite SystemCache."""
    def __init__(self, db: Session):
        self.db = db

    def get(self, key: str) -> Optional[Any]:
        """Fetches values from system cache checking expiry dates."""
        rec = self.db.query(SystemCache).filter(SystemCache.key == key).first()
        if not rec:
            return None
            
        if rec.expires_at and rec.expires_at < get_utc_now():
            self.db.delete(rec)
            self.db.commit()
            return None
            
        try:
            return json.loads(rec.value)
        except Exception:
            return rec.value

    def set(self, key: str, value: Any, ttl_seconds: Optional[int] = None):
        """Saves a query payload value in SQLite cache database."""
        val_str = json.dumps(value)
        expiry = get_utc_now() + ttl_seconds if ttl_seconds else None
        
        rec = SystemCache(key=key, value=val_str, expires_at=expiry)
        self.db.merge(rec)
        self.db.commit()

    def delete(self, key: str):
        """Invalidates a cache entry."""
        rec = self.db.query(SystemCache).filter(SystemCache.key == key).first()
        if rec:
            self.db.delete(rec)
            self.db.commit()
