from pydantic import BaseModel, Field
from typing import List, Optional

class InterviewStartRequest(BaseModel):
    project_path: str

class InterviewStartResponse(BaseModel):
    interview_id: str
    qa_id: str
    question: str
    type: str = "technical"
    focus_area: str = "General"

class AnswerSubmitRequest(BaseModel):
    interview_id: str
    qa_id: str
    user_answer: str
    project_path: str

class ScorecardResponse(BaseModel):
    score: int = Field(..., ge=0, le=100)
    missing_keywords: List[str] = []
    model_answer: str
    suggestions: str

class AnswerSubmitResponse(BaseModel):
    evaluation: ScorecardResponse
    next_question: InterviewStartResponse
