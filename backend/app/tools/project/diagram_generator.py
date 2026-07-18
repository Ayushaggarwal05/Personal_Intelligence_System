from sqlalchemy.orm import Session
from app.database.models.symbol import Symbol
from app.database.models.file import File

class DiagramGenerator:
    """Deterministic tool generating Mermaid.js diagrams from project symbols."""
    def __init__(self):
        pass

    def generate_er_diagram(self, db: Session, project_id: str) -> str:
        """Generates a Mermaid ER diagram illustrating project models schemas."""
        symbols = db.query(Symbol).join(File).filter(
            File.project_id == project_id,
            Symbol.type == "class"
        ).all()

        lines = ["erDiagram"]
        if not symbols:
            # Fallback default schema relations
            lines.append("    PROJECT ||--o{ FILE : contains")
            lines.append("    FILE ||--o{ SYMBOL : declares")
            lines.append("    INTERVIEW ||--o{ INTERVIEW_QA : records")
        else:
            # Map classes/entities to attributes
            for sym in symbols:
                lines.append(f"    {sym.name} {{")
                lines.append("        string id")
                lines.append("        string type")
                lines.append("    }")
                # Mock relationship to File entity
                lines.append(f"    FILE ||--o{{ {sym.name} : defines")

        return "\n".join(lines)

    def generate_api_flow(self, db: Session, project_id: str) -> str:
        """Generates a Mermaid graph diagram mapping API routes flow configurations."""
        routes = db.query(Symbol).join(File).filter(
            File.project_id == project_id,
            Symbol.type == "route"
        ).all()

        lines = ["graph LR"]
        if not routes:
            lines.append("    Client --> Route[\"GET /health\"]")
        else:
            for idx, route in enumerate(routes):
                node_id = f"route_{idx}"
                lines.append(f"    Client --> {node_id}[\"{route.name}: {route.signature}\"]")

        return "\n".join(lines)

    def generate_sequence_diagram(self, db: Session, project_id: str) -> str:
        """Generates a Mermaid sequence diagram illustrating the request-response controller lifecycle."""
        lines = [
            "sequenceDiagram",
            "    actor Client",
            "    participant Router as API Router",
            "    participant Service as Business Service",
            "    participant Repo as DB Repository",
            "    participant DB as SQLite Database",
            "",
            "    Client->>Router: HTTP Request",
            "    Router->>Service: Execute business transactions",
            "    Service->>Repo: Query SQL database",
            "    Repo->>DB: SQL Execution",
            "    DB-->>Repo: SQL Records",
            "    Repo-->>Service: Return ORM models",
            "    Service-->>Router: Format response payload",
            "    Router-->>Client: HTTP JSON Response"
        ]
        return "\n".join(lines)

diagram_generator = DiagramGenerator()
