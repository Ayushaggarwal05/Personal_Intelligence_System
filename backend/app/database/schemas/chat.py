from pydantic import BaseModel
from typing import Optional

class ChatMessageCreate(BaseModel):
    project_id: str
    message: str

class ChatMessageResponse(BaseModel):
    id: str
    project_id: str
    role: str
    content: str
    timestamp: int

    class Config:
        from_attributes = True
