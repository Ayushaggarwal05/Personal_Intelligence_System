import time
from sqlalchemy import Column, String, Integer, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.database.session import Base

class Interview(Base):
    __tablename__ = "interviews"

    id = Column(String, primary_key=True, index=True) # UUID
    project_id = Column(String, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    status = Column(String, default="active") # "active", "completed"
    score = Column(Integer, nullable=True) # Overall score graded by ReviewAgent
    created_at = Column(Integer, default=lambda: int(time.time()))

    # Relationships
    project = relationship("Project", back_populates="interviews")
    qa_records = relationship("InterviewQA", back_populates="interview", cascade="all, delete-orphan")

class InterviewQA(Base):
    __tablename__ = "interview_qa"

    id = Column(String, primary_key=True, index=True) # UUID
    interview_id = Column(String, ForeignKey("interviews.id", ondelete="CASCADE"), nullable=False)
    question = Column(Text, nullable=False)
    user_answer = Column(Text, nullable=True)
    feedback_json = Column(Text, nullable=True) # Stores JSON metadata: missing keywords, score, model answer, suggestions
    timestamp = Column(Integer, default=lambda: int(time.time()))

    # Relationships
    interview = relationship("Interview", back_populates="qa_records")
