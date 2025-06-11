from uuid import uuid4
from typing import List, Dict
from pydantic import BaseModel, Field

from chunk import Chunk

class Document(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    chunks : List[Chunk] = Field(default = [], description="Chunks of text within this document.")
    metadata: Dict[str, str]