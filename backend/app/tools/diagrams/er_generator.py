from app.tools.project.diagram_generator import diagram_generator

def generate_er_mermaid(db, project_id: str) -> str:
    """Generates Entity-Relationship diagrams in Mermaid.js syntax."""
    return diagram_generator.generate_er_diagram(db, project_id)
