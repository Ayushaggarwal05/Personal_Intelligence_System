from app.orchestrator.model_router import model_router
from typing import Optional

def generate_gemini(prompt: str, system_prompt: Optional[str] = None, json_format: bool = False) -> str:
    """Invokes the cloud Gemini API provider."""
    from app.core.settings import settings
    original = settings.ACTIVE_LLM_PROVIDER
    settings.ACTIVE_LLM_PROVIDER = "gemini"
    try:
        return model_router.generate(prompt, system_prompt, json_format)
    finally:
        settings.ACTIVE_LLM_PROVIDER = original
