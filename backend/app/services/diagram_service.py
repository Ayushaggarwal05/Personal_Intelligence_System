from sqlalchemy.orm import Session
from app.tools.project.diagram_generator import diagram_generator

class DiagramService:
    """Service class encapsulating Mermaid.js diagram drawing tasks."""
    def __init__(self, db: Session):
        self.db = db

    def get_er_code(self, project_id: str) -> str:
        return diagram_generator.generate_er_diagram(self.db, project_id)

    def get_sequence_code(self, project_id: str) -> str:
        return diagram_generator.generate_sequence_diagram(self.db, project_id)

    def get_api_flow_code(self, project_id: str) -> str:
        return diagram_generator.generate_api_flow(self.db, project_id)
