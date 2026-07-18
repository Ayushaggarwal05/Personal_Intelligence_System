from typing import Optional
from pydantic import BaseModel, Field

class LocalModelConfig(BaseModel):
    host: str = "http://localhost:11434"
    model_name: str = "qwen2.5:3b-instruct"
    temperature: float = 0.2
    context_window: int = 16384

class CloudModelConfig(BaseModel):
    api_key: Optional[str] = None
    model_name: str = "gemini-1.5-flash"
    temperature: float = 0.2
    max_tokens: int = 4096
    request_timeout: int = 60

class EmbeddingsConfig(BaseModel):
    model_name: str = "all-MiniLM-L6-v2"
    device: str = "cpu"
    cache_folder: Optional[str] = None

class ModelConfig(BaseModel):
    local: LocalModelConfig = Field(default_factory=LocalModelConfig)
    cloud: CloudModelConfig = Field(default_factory=CloudModelConfig)
    embeddings: EmbeddingsConfig = Field(default_factory=EmbeddingsConfig)

model_config = ModelConfig()
