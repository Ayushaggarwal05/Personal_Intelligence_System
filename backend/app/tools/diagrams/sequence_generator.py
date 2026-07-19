from app.tools.project.diagram_generator import diagram_generator

def generate_sequence_mermaid(db, project_id: str) -> str:
    """Generates controller sequences diagrams in Mermaid.js syntax."""
    return diagram_generator.generate_sequence_diagram(db, project_id)
