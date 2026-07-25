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
        """Generates exactly 3 codebase-specific learning path follow-up questions the user should ask ASTA next."""
        project_name = context.get("project_name", "Project")
        framework = context.get("framework", "Python")
        database_type = context.get("database_type", "SQLite")
        symbols = context.get("symbols", "")

        prompt = (
            f"You are the ASTA Learning Path Generator Agent.\n"
            f"Based on the following technical explanation of the '{project_name}' project, generate exactly 2 progressive technical questions that the user should ask ASTA next to deepen their codebase understanding.\n\n"
            f"# Tech Stack:\n"
            f"- Framework: {framework}\n"
            f"- Database: {database_type}\n\n"
            f"# Codebase Symbols Context:\n"
            f"{symbols}\n\n"
            f"# Recent Technical Explanation Given:\n"
            f"{explanation}\n\n"
            f"# INSTRUCTIONS:\n"
            f"- Generate exactly 2 codebase-grounded technical questions related directly to the stack and codebase context above.\n"
            f"- The questions must NOT be quiz questions for the user to answer. They must be questions for the user to ask ASTA next to learn more (e.g. 'Why did we choose X over Y?', 'How is Z pattern implemented here?').\n"
            f"- Structure the questions to progressively deepen understanding (e.g., Question 1 focuses on design choices, Question 2 focuses on scaling/locking details).\n"
            f"- Format the output strictly as:\n"
            f"To deepen your understanding of this topic, consider asking:\n\n"
            f"1. [First progressive learning question]\n\n"
            f"2. [Second progressive learning question]\n"
            f"- Do not include any markdown headers (no '#', no '##'), introductory remarks, system thoughts, or markdown code-block wraps."
        )

        response = self.call_llm(prompt=prompt)
        return response
