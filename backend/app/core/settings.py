import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings

# Resolve paths relative to backend root
BACKEND_ROOT = Path(__file__).resolve().parent.parent.parent

class Settings(BaseSettings):
    PROJECT_NAME: str = "Personal Engineering Intelligence System"
    VERSION: str = "1.0.0"
    
    # Storage & Log Paths
    STORAGE_DIR: str = str(BACKEND_ROOT / "storage")
    LOGS_DIR: str = str(BACKEND_ROOT / "storage" / "logs")
    DATABASE_URL: str = f"sqlite:///{BACKEND_ROOT}/storage/peis.db"
    LANCEDB_URI: str = str(BACKEND_ROOT / "storage" / "cache" / "lancedb")
    
    # Prompt Directory (located at backend root, as per requirements)
    PROMPTS_ROOT: str = str(BACKEND_ROOT / "prompts")
    
    # LLM configurations
    OLLAMA_HOST: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "qwen2.5:3b-instruct"
    
    GROQ_API_KEY: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None
    OPENROUTER_API_KEY: Optional[str] = None
    
    # Active LLM Provider: "local" or "groq" or "gemini" or "openrouter"
    ACTIVE_LLM_PROVIDER: str = "local"
    
    # Embeddings Configurations
    EMBEDDINGS_MODEL_NAME: str = "all-MiniLM-L6-v2"
    
    # System logging
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = str(BACKEND_ROOT / ".env")
        env_file_encoding = "utf-8"
        case_sensitive = True

settings = Settings()

# Ensure critical backend storage directories exist
os.makedirs(settings.STORAGE_DIR, exist_ok=True)
os.makedirs(settings.LOGS_DIR, exist_ok=True)
os.makedirs(settings.PROMPTS_ROOT, exist_ok=True)
os.makedirs(settings.LANCEDB_URI, exist_ok=True)
os.makedirs(os.path.dirname(settings.DATABASE_URL.replace("sqlite:///", "")), exist_ok=True)
