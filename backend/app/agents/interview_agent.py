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

        # Fetch developer's weak topics from past interview evaluations
        from app.database.repositories.interview_repository import InterviewRepository, InterviewQARepository
        from app.agents.memory_agent import MemoryAgent
        mem_agent = MemoryAgent(db)
        weak_topics = mem_agent.extract_user_weak_areas(project.id)
        
        weak_topics_summary = ""
        if weak_topics:
            weak_topics_summary = f"\n\nDeveloper's Frequently Missed Technical Concepts:\n- " + "\n- ".join(weak_topics[:5])

        # Fetch recent git diff modifications
        git_changes = get_git_diff_patch(project.path, count=1)

        # 2. Setup Prompt Variables
        variables = {
            "project_name": project.name,
            "framework": project.framework or "Python/FastAPI",
            "database_type": project.database_type or "SQLite",
            "symbols": symbols_summary + weak_topics_summary,
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

    def generate_chat_followup_questions(self, context: dict, explanation: str) -> str:
        """Generates 3 codebase-specific follow-up questions relevant to the Technical Interview Mentor's explanation."""
        project_name = context.get("project_name", "Project")
        framework = context.get("framework", "Python")
        database_type = context.get("database_type", "SQLite")
        symbols = context.get("symbols", "")

        prompt = (
            f"You are the PEIS Interview Coach Agent.\n"
            f"Based on the following technical explanation of the '{project_name}' project, generate 3 highly targeted technical interview follow-up questions.\n\n"
            f"# Tech Stack:\n"
            f"- Framework: {framework}\n"
            f"- Database: {database_type}\n\n"
            f"# Codebase Symbols Context:\n"
            f"{symbols}\n\n"
            f"# Recent Technical Explanation Given:\n"
            f"{explanation}\n\n"
            f"# INSTRUCTIONS:\n"
            f"- Generate 3 challenging, codebase-grounded technical questions related to the explanation above.\n"
            f"- The questions should test the developer's knowledge on architectural choices, database connection limits, API payload validation, or scaling/security patterns of their project.\n"
            f"- Format the output as a clean, list of 3 items (e.g. 1. Question, 2. Question, 3. Question). Prefix the block with a '## ❓ Likely Follow-up Questions' markdown header. Do not include any code wrappers or system instructions."
        )

        response = self.call_llm(prompt=prompt)
        return response
