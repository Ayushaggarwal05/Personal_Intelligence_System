from sqlalchemy import Column, String, Integer, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.database.session import Base

class File(Base):
    __tablename__ = "files"

    id = Column(String, primary_key=True, index=True) # UUID or hash of relative path
    project_id = Column(String, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    relative_path = Column(String, nullable=False, index=True) # Path relative to project root
    file_hash = Column(String, nullable=False) # SHA-256 hash of file contents
    last_modified = Column(Integer, nullable=False) # Timestamp from filesystem
    token_count = Column(Integer, default=0)
    summary = Column(Text, nullable=True) # AI-generated short description of this file

    # Relationships
    project = relationship("Project", back_populates="files")
    symbols = relationship("Symbol", back_populates="file", cascade="all, delete-orphan")
