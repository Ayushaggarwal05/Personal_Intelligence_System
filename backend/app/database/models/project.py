import time
from sqlalchemy import Column, String, Integer, Text
from sqlalchemy.orm import relationship
from app.database.session import Base

class Project(Base):
    __tablename__ = "projects"

    id = Column(String, primary_key=True, index=True) # UUID or hash
    name = Column(String, nullable=False)
    path = Column(String, unique=True, nullable=False, index=True) # Full filesystem path
    framework = Column(String, nullable=True) # e.g. FastAPI, Express
    database_type = Column(String, nullable=True) # e.g. SQLite, MongoDB
    summary = Column(Text, nullable=True) # Main summary of what the project does
    
    created_at = Column(Integer, default=lambda: int(time.time()))
    updated_at = Column(Integer, default=lambda: int(time.time()), onupdate=lambda: int(time.time()))

    # Relationships
    files = relationship("File", back_populates="project", cascade="all, delete-orphan")
    interviews = relationship("Interview", back_populates="project", cascade="all, delete-orphan")
