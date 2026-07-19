import os
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from app.core.settings import settings
from app.core.workspace_config import workspace_config

router = APIRouter(prefix="/settings", tags=["Configuration Settings"])

class KeyConfigRequest(BaseModel):
    gemini_key: Optional[str] = None
    groq_key: Optional[str] = None

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
        "has_gemini_key": bool(settings.GEMINI_API_KEY),
        "has_groq_key": bool(settings.GROQ_API_KEY),
        "workspace_config": {
            "allowed_extensions": list(workspace_config.allowed_extensions),
            "max_file_size_bytes": workspace_config.max_file_size_bytes,
            "token_character_ratio": workspace_config.token_character_ratio
        }
    }

@router.post("/keys")
def update_application_keys(payload: KeyConfigRequest):
    """Updates the Gemini/Groq API keys in memory and persists them in the local .env configuration."""
    env_path = os.path.join(os.path.dirname(settings.STORAGE_DIR), ".env")
    
    def write_key(key_name: str, key_val: Optional[str]):
        if key_val is None:
            return
        val = key_val.strip()
        
        # Save in memory settings
        if key_name == "GEMINI_API_KEY":
            settings.GEMINI_API_KEY = val if val else None
        elif key_name == "GROQ_API_KEY":
            settings.GROQ_API_KEY = val if val else None
            
        # Write back to physical .env file
        lines = []
        if os.path.exists(env_path):
            with open(env_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
                
        replaced = False
        new_lines = []
        for line in lines:
            if line.strip().startswith(f"{key_name}="):
                new_lines.append(f"{key_name}={val}\n")
                replaced = True
            else:
                new_lines.append(line)
        if not replaced:
            new_lines.append(f"{key_name}={val}\n")
            
        with open(env_path, "w", encoding="utf-8") as f:
            f.writelines(new_lines)

    write_key("GEMINI_API_KEY", payload.gemini_key)
    write_key("GROQ_API_KEY", payload.groq_key)
    
    return {
        "success": True,
        "message": "API keys successfully updated and written to local configuration.",
        "has_gemini_key": bool(settings.GEMINI_API_KEY),
        "has_groq_key": bool(settings.GROQ_API_KEY)
    }
