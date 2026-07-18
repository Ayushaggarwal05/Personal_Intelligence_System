from fastapi import APIRouter, Body
from app.core.settings import settings
from app.core.workspace_config import workspace_config

router = APIRouter(prefix="/settings", tags=["Configuration Settings"])

@router.get("")
def get_application_settings():
    """Returns application environment settings configurations."""
    return {
        "project_name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "storage_dir": settings.STORAGE_DIR,
        "database_url": settings.DATABASE_URL,
        "logs_dir": settings.LOGS_DIR,
        "prompts_root": settings.PROMPTS_ROOT,
        "active_llm_provider": settings.ACTIVE_LLM_PROVIDER,
        "ollama_host": settings.OLLAMA_HOST,
        "ollama_model": settings.OLLAMA_MODEL,
        "embeddings_model_name": settings.EMBEDDINGS_MODEL_NAME,
        "log_level": settings.LOG_LEVEL,
        "workspace_config": {
            "allowed_extensions": list(workspace_config.allowed_extensions),
            "max_file_size_bytes": workspace_config.max_file_size_bytes,
            "token_character_ratio": workspace_config.token_character_ratio
        }
    }

@router.post("/provider")
def update_llm_provider(
    provider: str = Body(..., embed=True)
):
    """Updates the active LLM provider configurations."""
    allowed = {"local", "gemini", "groq", "openrouter"}
    val = provider.strip().lower()
    if val not in allowed:
        return {"success": False, "error": f"Invalid provider. Must be one of: {allowed}"}
        
    settings.ACTIVE_LLM_PROVIDER = val
    return {
        "success": True, 
        "message": f"LLM provider updated to: {val}",
        "active_llm_provider": settings.ACTIVE_LLM_PROVIDER
    }
