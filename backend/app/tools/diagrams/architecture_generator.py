from app.tools.project.diagram_generator import diagram_generator

def generate_architecture_mermaid(db, project_id: str) -> str:
    """Generates architecture diagrams in Mermaid.js syntax."""
    return diagram_generator.generate_sequence_diagram(db, project_id)
