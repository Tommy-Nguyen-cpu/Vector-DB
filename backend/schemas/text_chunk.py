from uuid import uuid4
from typing import List, Dict
from pydantic import BaseModel, Field

class TextChunk(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    text : str = Field(default = "", description="Text associated with the chunk.")
    embeddings : List[float] = Field(default = [], description="The embedding of the text.")
    metadata: Dict[str, str]