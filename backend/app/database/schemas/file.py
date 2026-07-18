from pydantic import BaseModel
from typing import Optional

class FileResponse(BaseModel):
    id: str
    project_id: str
    relative_path: str
    file_hash: str
    last_modified: int
    token_count: int
    summary: Optional[str] = None

    class Config:
        from_attributes = True
