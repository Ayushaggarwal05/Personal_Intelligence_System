from app.orchestrator.model_router import model_router
from typing import Optional

def generate_local(prompt: str, system_prompt: Optional[str] = None, json_format: bool = False) -> str:
    """Invokes the local Ollama LLM provider."""
    # Force settings active provider to local for this wrapper block
    from app.core.settings import settings
    original = settings.ACTIVE_LLM_PROVIDER
    settings.ACTIVE_LLM_PROVIDER = "local"
    try:
        return model_router.generate(prompt, system_prompt, json_format)
    finally:
        settings.ACTIVE_LLM_PROVIDER = original
