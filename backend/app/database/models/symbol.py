from sqlalchemy import Column, String, Integer, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.database.session import Base

class Symbol(Base):
    __tablename__ = "symbols"

    id = Column(String, primary_key=True, index=True) # UUID or hash
    file_id = Column(String, ForeignKey("files.id", ondelete="CASCADE"), nullable=False)
    name = Column(String, nullable=False, index=True) # e.g. function name, class name
    type = Column(String, nullable=False) # "class", "function", "route", "model"
    signature = Column(Text, nullable=True) # e.g. def parse_text(data: str) -> dict
    docstring = Column(Text, nullable=True) # docstring or comments inside
    line_start = Column(Integer, nullable=False)
    line_end = Column(Integer, nullable=False)

    # Relationships
    file = relationship("File", back_populates="symbols")
