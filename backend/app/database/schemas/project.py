from pydantic import BaseModel
from typing import Optional

class ProjectBase(BaseModel):
    name: str
    path: str
    framework: Optional[str] = None
    database_type: Optional[str] = None

class ProjectCreate(ProjectBase):
    pass

class ProjectResponse(ProjectBase):
    id: str
    summary: Optional[str] = None
    created_at: int
    updated_at: int

    class Config:
        from_attributes = True

class ProjectScanRequest(BaseModel):
    path: str
