from typing import List, Dict

from Common.schemas.document import Document
from Common.schemas.text_chunk import TextChunk

def get_docid_chunk_dict(documents : List[Document]) -> Dict[str, List[TextChunk]]:
    chunks = {}
    for doc in documents:
        chunks.setdefault(doc.id, [chunk for chunk in doc.chunks.values()])
    
    return chunks