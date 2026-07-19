from app.tools.project.diagram_generator import diagram_generator

def generate_flow_mermaid(db, project_id: str) -> str:
    """Generates flowchart diagrams mapping API endpoints in Mermaid.js syntax."""
    return diagram_generator.generate_api_flow(db, project_id)
