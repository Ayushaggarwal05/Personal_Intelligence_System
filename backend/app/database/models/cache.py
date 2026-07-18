from sqlalchemy import Column, String, Integer
from app.database.session import Base

class SystemCache(Base):
    __tablename__ = "system_cache"

    key = Column(String, primary_key=True, index=True) # key namespace
    value = Column(String, nullable=False) # JSON or serialized string
    expires_at = Column(Integer, nullable=True) # Unix timestamp expiry (Optional)
