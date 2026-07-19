from sqlalchemy.orm import Session
from app.orchestrator.workflow import WorkflowEngine

class InterviewService:
    """Service class executing mock interview generate and evaluation flows."""
    def __init__(self, db: Session):
        self.db = db
        self.engine = WorkflowEngine(db)

    def start_mock_interview(self, project_id: str) -> dict:
        return self.engine.run_interview_generate_workflow(project_id)

    def review_mock_answer(self, interview_id: str, qa_id: str, answer: str, project_id: str) -> dict:
        return self.engine.run_interview_review_workflow(interview_id, qa_id, answer, project_id)
