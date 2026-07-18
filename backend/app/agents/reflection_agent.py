from sqlalchemy.orm import Session
from app.database.models.project import Project
from app.database.models.file import File
from app.database.models.symbol import Symbol
from app.core.logging import logger
import re

class ReflectionAgent:
    def __init__(self):
        self.name = "ReflectionAgent"

    def validate_review_scorecard(self, context: dict, scorecard: dict) -> dict:
        """Audits the graded scorecard to ensure suggested code blocks/symbols exist in codebase."""
        db: Session = context["db"]
        project_path = context["project_path"]
        
        project = db.query(Project).filter(Project.path == project_path).first()
        if not project:
            return scorecard

        # Retrieve a list of all actual symbol names currently stored in SQLite
        db_symbols = db.query(Symbol).join(File).filter(File.project_id == project.id).all()
        actual_symbol_names = {s.name.lower() for s in db_symbols}
        actual_route_paths = {s.signature.lower() for s in db_symbols if s.type == "route"}

        # Audit missing keywords to ensure they represent reasonable patterns,
        # and remove/adjust any highly specific symbol names if the LLM hallucinated them.
        validated_keywords = []
        for kw in scorecard.get("missing_keywords", []):
            kw_lower = kw.lower().strip()
            # If LLM suggests a specific symbol (e.g. userAuthService) check if it actually exists in SQLite.
            # If not, and it looks like code, we generalize it or discard it.
            if re.match(r'^[a-zA-Z0-9_]+$', kw_lower) and len(kw_lower) > 5:
                if kw_lower in actual_symbol_names:
                    validated_keywords.append(kw)
                else:
                    logger.info(f"[ReflectionAgent] Dropped hallucinated symbol keyword: '{kw}'")
            else:
                # Keep general concepts like "connection pooling", "JWT"
                validated_keywords.append(kw)

        scorecard["missing_keywords"] = validated_keywords
        return scorecard

reflection_agent = ReflectionAgent()
