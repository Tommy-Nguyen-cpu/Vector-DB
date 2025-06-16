from uuid import uuid4
from typing import List, Dict
from pydantic import BaseModel, Field

from .document import Document

class Library(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    documents : List[Document] = Field(default = [], description="All documents within this library.")
    metadata: Dict[str, str]
    class Config:
        orm_mode = True