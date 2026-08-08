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
        super().__init__(name="InterviewAgent", category="interview", prompt_file="chat_followup.txt")

    def generate_chat_followup_questions(self, context: dict, explanation: str) -> str:
        """Generates exactly 2 codebase-specific progressive follow-up questions the user should ask ASTA next."""
        from app.services.prompt_loader import prompt_loader
        
        project_name = context.get("project_name", "Project")
        framework = context.get("framework", "Python")
        database_type = context.get("database_type", "SQLite")
        symbols = context.get("symbols", "")

        variables = {
            "project_name": project_name,
            "framework": framework,
            "database_type": database_type,
            "symbols": symbols
        }

        # Load and validate the dedicated template
        system_prompt = prompt_loader.load_prompt("interview", "chat_followup.txt")
        prompt_loader.validate_prompt_variables("interview", "chat_followup.txt", system_prompt)
        system_prompt_hydrated = system_prompt.format(**variables)

        # Prompt instruction
        prompt = f"# Recent Technical Explanation Given:\n{explanation}\n\nGenerate exactly 2 progressive learning follow-up questions now."

        # Execute query using the unified model router
        response = self.router.generate(prompt=prompt, system_prompt=system_prompt_hydrated)
        return response
