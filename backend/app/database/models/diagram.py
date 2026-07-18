import time
from sqlalchemy import Column, String, Integer, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.database.session import Base

class Diagram(Base):
    __tablename__ = "diagrams"

    id = Column(String, primary_key=True, index=True) # UUID or hash
    project_id = Column(String, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    type = Column(String, nullable=False) # "architecture", "er", "sequence", "flow"
    mermaid_code = Column(Text, nullable=False) # Mermaid.js markup
    created_at = Column(Integer, default=lambda: int(time.time()))

    # Relationships
    project = relationship("Project")
