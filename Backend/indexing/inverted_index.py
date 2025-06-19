from typing import List, Dict, Tuple
from Common.schemas.text_chunk import TextChunk

class InvertedIndex:
    """
    Simple inverted index over chunk texts.
    Maps term -> set of (document_id, chunk_id)
    """
    def __init__(self):
        self.index: Dict[str, set] = {} # Keeps track of all unique tokens (words) and the corresponding documents and chunks they reside in.

    def add_chunk(self, library_id : str, doc_id: str, chunk: TextChunk):
        tokens = chunk.text.lower().split() # Normalize text so casing does not play a major role. Split on per word, since most queries are based on a per-word basis, not sentence level.
        for token in tokens:
            if token not in self.index:
                self.index[token] = set() # Store unique Ids.
            self.index[token].add((library_id, doc_id, chunk.id)) # Add doc and chunk id to index. Will update if I think library is worth storing as well.

    def search(self, term: str) -> List[Tuple[str, str, str]]:
        return list(self.index.get(term.lower(), [])) # Gets all document and chunk ids associated with a token.
