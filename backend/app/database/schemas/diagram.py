from pydantic import BaseModel

class DiagramCreate(BaseModel):
    project_id: str
    type: str # "architecture", "er", "sequence", "flow"
    mermaid_code: str

class DiagramResponse(BaseModel):
    id: str
    project_id: str
    type: str
    mermaid_code: str
    created_at: int

    class Config:
        from_attributes = True
