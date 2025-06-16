from uuid import uuid4
from typing import List, Dict
from pydantic import BaseModel, Field

from .text_chunk import TextChunk

class Document(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    chunks : List[TextChunk] = Field(default = [], description="Chunks of text within this document.")
    metadata: Dict[str, str]
    class Config:
        orm_mode = True