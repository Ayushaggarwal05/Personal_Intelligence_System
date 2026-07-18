from pydantic import BaseModel
from typing import Optional

class SymbolResponse(BaseModel):
    id: str
    file_id: str
    name: str
    type: str # "class", "function", "route", "model"
    signature: Optional[str] = None
    docstring: Optional[str] = None
    line_start: int
    line_end: int

    class Config:
        from_attributes = True
