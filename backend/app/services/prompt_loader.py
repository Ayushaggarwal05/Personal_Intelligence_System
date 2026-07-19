import os
import re
from typing import Dict, List, Optional
from app.core.settings import settings
from app.core.logging import logger

class PromptLoaderService:
    """Service to dynamically load, cache, and validate system prompts from backend/prompts/."""
    def __init__(self):
        self.prompts_dir = settings.PROMPTS_ROOT
        os.makedirs(self.prompts_dir, exist_ok=True)
        # In-memory cache to prevent repeated disk access
        self._cache: Dict[str, str] = {}
        
        # Expected variables registry for validation
        self._registry: Dict[str, List[str]] = {
            "chat/system_prompt.txt": ["project_context"],
            "interview/generate_q.txt": ["project_name", "framework", "database_type", "symbols", "git_changes"],
            "interview/score_answer.txt": ["framework", "database_type", "symbols", "question", "user_answer"],
            "planner/plan.txt": ["user_intent"]
        }

    def load_prompt(self, category: str, name: str) -> str:
        """Loads prompt from in-memory cache or files, writing default placeholder if missing."""
        cache_key = f"{category}/{name}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        category_dir = os.path.join(self.prompts_dir, category)
        os.makedirs(category_dir, exist_ok=True)
        
        prompt_file_path = os.path.join(category_dir, name)
        
        content = ""
        if os.path.exists(prompt_file_path):
            try:
                with open(prompt_file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                logger.info(f"Loaded prompt template '{category}/{name}' from disk.")
            except Exception as e:
                logger.error(f"Error reading prompt file {prompt_file_path}: {e}")
                
        if not content:
            # Fallback default template definitions based on registry
            content = self._get_default_template(cache_key)
            try:
                with open(prompt_file_path, "w", encoding="utf-8") as f:
                    f.write(content)
                logger.info(f"Created fallback template prompt at {prompt_file_path}")
            except Exception as e:
                logger.error(f"Failed to write template prompt file: {e}")

        # Store in cache
        self._cache[cache_key] = content
        return content

    def validate_prompt_variables(self, category: str, name: str, prompt_text: str) -> bool:
        """Verifies if the loaded prompt text contains the registered template variables."""
        cache_key = f"{category}/{name}"
        expected_vars = self._registry.get(cache_key, [])
        
        # Find all brackets placeholders like {variable_name}
        found_vars = set(re.findall(r'\{([a-zA-Z0-9_]+)\}', prompt_text))
        
        missing = [v for v in expected_vars if v not in found_vars]
        if missing:
            logger.warning(f"Prompt '{cache_key}' is missing registered placeholders: {missing}")
            return False
        return True

    def clear_cache(self):
        """Clears the prompt cache."""
        self._cache.clear()

    def _get_default_template(self, key: str) -> str:
        """Returns standard system instruction prompts optimized for technical interviews."""
        if key == "chat/system_prompt.txt":
            return (
                "You are the PEIS Technical Explanation Agent.\n"
                "Your objective is to explain the codebase in a way that helps a developer pass a technical interview.\n"
                "Focus on engineering choices, trade-offs, architecture, and libraries used.\n"
                "Here is the context of the project:\n"
                "{project_context}\n"
            )
        elif key == "interview/generate_q.txt":
            return (
                "You are the PEIS Mock Interview Coach.\n"
                "Based on the project structure, generate one interview question (Technical, Design, or Trade-off) for {project_name}.\n"
                "Project framework: {framework}\n"
                "Project database: {database_type}\n"
                "Indexed code structures:\n"
                "{symbols}\n"
                "Recent Git changes:\n"
                "{git_changes}\n"
                "Return a JSON format containing keys 'question', 'focus_area', 'type'.\n"
            )
        elif key == "interview/score_answer.txt":
            return (
                "You are the PEIS Senior Interviewer grading engine.\n"
                "Evaluate the developer's answer relative to the project context and correct technical definitions.\n"
                "Project framework: {framework}\n"
                "Project database: {database_type}\n"
                "Indexed code structures:\n"
                "{symbols}\n"
                "Question: {question}\n"
                "Developer Answer: {user_answer}\n"
                "Provide suggestions, score (0-100), missing keywords/concepts, and a model senior-level answer.\n"
                "Return valid JSON containing keys 'score', 'suggestions', 'missing_keywords', 'model_answer'.\n"
            )
        elif key == "planner/plan.txt":
            return (
                "You are the PEIS Swarm Orchestrator Planner.\n"
                "Decompose user intent into execution steps.\n"
                "User query: {user_intent}\n"
                "Determine if we need 'retrieval', 'project_details', 'interview', or 'chat'.\n"
                "Return a JSON list of steps.\n"
            )
        else:
            return (
                f"# PEIS Default System Template for {key}\n"
                "Answer technical queries focusing on tradeoffs and architectural patterns.\n"
            )

prompt_loader = PromptLoaderService()
