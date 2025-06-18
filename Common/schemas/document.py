from uuid import uuid4
from typing import List, Dict
from pydantic import BaseModel, Field

from .text_chunk import TextChunk

class Document(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    chunks : Dict[str, TextChunk] = Field(default = {}, description="Chunks of text within this document, mapped by chunk_id.")
    metadata: Dict[str, str]