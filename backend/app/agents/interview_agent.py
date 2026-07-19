import json
from app.agents.base_agent import BaseAgent
from app.database.models.project import Project
from app.database.models.file import File
from app.database.models.symbol import Symbol
from app.core.logging import logger
from app.core.exceptions import PEISException

from app.tools.git.history import get_git_diff_patch

class InterviewAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="InterviewAgent", category="interview", prompt_file="generate_q.txt")

    def generate_question(self, context: dict) -> dict:
        """Generates a project-specific interview question based on the indexed symbols tree and git updates."""
        db = context["db"]
        project_path = context["project_path"]

        project = db.query(Project).filter(Project.path == project_path).first()
        if not project:
            raise PEISException(f"Project not found at path '{project_path}'", status_code=404)

        # 1. Fetch some symbols to provide context
        db_symbols = db.query(Symbol).join(File).filter(File.project_id == project.id).limit(15).all()
        
        symbols_summary = ""
        if db_symbols:
            symbols_summary = "\n".join([
                f"- [{s.type.upper()}] Name: {s.name} | Signature: {s.signature}" 
                for s in db_symbols
            ])
        else:
            symbols_summary = "No files or functions indexed yet. Ask general technical questions about building projects."

        # Fetch recent git diff modifications
        git_changes = get_git_diff_patch(project.path, count=1)

        # 2. Setup Prompt Variables
        variables = {
            "project_name": project.name,
            "framework": project.framework or "Python/FastAPI",
            "database_type": project.database_type or "SQLite",
            "symbols": symbols_summary,
            "git_changes": git_changes
        }

        logger.info(f"[InterviewAgent] Generating mock question for project: {project.name}")
        
        try:
            # Call LLM router requesting JSON output
            raw_response = self.call_llm(
                prompt="Generate a mock interview question now.",
                system_variables=variables,
                json_format=True
            )
            logger.info(f"[InterviewAgent] Raw LLM Response: {raw_response}")
            
            # Clean string in case of trailing code block markers
            cleaned_res = raw_response.strip()
            if cleaned_res.startswith("```"):
                cleaned_res = cleaned_res.split("\n", 1)[1].rsplit("```", 1)[0].strip()
                if cleaned_res.startswith("json"):
                    cleaned_res = cleaned_res[4:].strip()
                    
            question_data = json.loads(cleaned_res)
            return question_data
        except Exception as e:
            logger.error(f"[InterviewAgent] Failed to generate/parse LLM question: {e}. Booting fallback question.")
            # Resilient fallback question based on framework and DB settings
            return {
                "question": f"Explain the architectural pattern you used in this {project.framework or 'FastAPI'} application, and how it handles request lifecycle or database connection management.",
                "type": "technical",
                "focus_area": "Architecture"
            }
