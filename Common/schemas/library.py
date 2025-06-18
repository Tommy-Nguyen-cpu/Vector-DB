from uuid import uuid4
from typing import List, Dict
from pydantic import BaseModel, Field

from .document import Document

class Library(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    documents : Dict[str, Document] = Field(default = {}, description="All documents within this library, mapped by doc_id.")
    metadata: Dict[str, str]