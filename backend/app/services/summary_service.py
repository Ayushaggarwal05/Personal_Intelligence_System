from sqlalchemy.orm import Session
from app.orchestrator.workflow import WorkflowEngine

class SummaryService:
    """Service class executing codebase architectural summaries workflows."""
    def __init__(self, db: Session):
        self.db = db
        self.engine = WorkflowEngine(db)

    def generate_project_summary(self, project_id: str, query: str = "Provide explanation") -> str:
        return self.engine.run_explain_workflow(project_id, query)
