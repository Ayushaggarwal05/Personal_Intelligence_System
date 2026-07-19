from sqlalchemy.orm import Session
from app.orchestrator.workflow import WorkflowEngine

class ReviewService:
    """Service class executing mock response reviews grading workflows."""
    def __init__(self, db: Session):
        self.db = db
        self.engine = WorkflowEngine(db)

    def evaluate_response(self, interview_id: str, qa_id: str, user_answer: str, project_id: str):
        return self.engine.run_interview_review_workflow(interview_id, qa_id, user_answer, project_id)
