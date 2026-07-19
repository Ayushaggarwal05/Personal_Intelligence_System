import os
import json
from typing import Optional, Dict, Any
from app.orchestrator.model_router import run_llm_generation
from app.core.settings import settings
from app.core.logging import logger
from app.core.base_interfaces import BaseAgentInterface
from app.services.prompt_loader import prompt_loader

class BaseAgent(BaseAgentInterface):
    """Execution wrapper for agents managing prompt templates hydration, model routing, and structured JSON parsing."""
    def __init__(self, name: str, category: str, prompt_file: str):
        self.name = name
        self.category = category
        self.prompt_file = prompt_file
        self.system_prompt_template = ""
        self._load_system_prompt()

    def _load_system_prompt(self):
        """Loads prompt template from centralized prompt loader service."""
        self.system_prompt_template = prompt_loader.load_prompt(self.category, self.prompt_file)
        # Validate that variables are registered/sound
        prompt_loader.validate_prompt_variables(self.category, self.prompt_file, self.system_prompt_template)

    def get_system_prompt(self, variables: Optional[Dict[str, Any]] = None) -> str:
        """Hydrates prompt templates placeholders with runtime context variables."""
        # Reload dynamically in case template changed on disk during active developer sessions
        self.system_prompt_template = prompt_loader.load_prompt(self.category, self.prompt_file)
        
        if not variables:
            return self.system_prompt_template
        try:
            return self.system_prompt_template.format(**variables)
        except KeyError as e:
            logger.warning(f"KeyError formatting prompt template for '{self.name}': missing key {e}.")
            return self.system_prompt_template
        except Exception as e:
            logger.error(f"Error formatting prompt template: {e}")
            return self.system_prompt_template

    def call_llm(self, prompt: str, system_variables: Optional[Dict[str, Any]] = None, json_format: bool = False, provider: Optional[str] = None) -> str:
        """Executes LLM generation pipeline using ModelRouter, capturing logs and durations."""
        logger.info(f"[{self.name}] Initiating model generation request...")
        system_prompt = self.get_system_prompt(system_variables)
        
        response = run_llm_generation(prompt=prompt, system_prompt=system_prompt, json_format=json_format, provider=provider)
        logger.info(f"[{self.name}] Model generation completed successfully.")
        return response

    def call_llm_structured(self, prompt: str, system_variables: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Call LLM and guarantees return of a valid JSON dictionary structure."""
        raw_res = self.call_llm(prompt, system_variables, json_format=True)
        try:
            # Strip any markdown wrappers like ```json ... ``` if model returned them
            clean_res = raw_res.strip()
            if clean_res.startswith("```json"):
                clean_res = clean_res[7:]
            if clean_res.endswith("```"):
                clean_res = clean_res[:-3]
            return json.loads(clean_res.strip())
        except Exception as e:
            logger.error(f"[{self.name}] Failed to parse structured JSON from LLM: {e}. Raw response: {raw_res}")
            # Fallback matching placeholder dictionary
            return {}
