from typing import List, Dict, Tuple
import traceback

from Common.schemas.text_chunk import TextChunk

class InvertedIndex:
    """
    Simple inverted index over chunk texts.
    Maps term -> set of (document_id, chunk_id)
    """
    def __init__(self):
        self.index: Dict[str, set] = {} # Keeps track of all unique tokens (words) and the corresponding documents and chunks they reside in.
        self.docs = set() # Just for our use case in verify if doc exists in API side.

    def add_chunk(self, library_id : str, doc_id: str, chunk: TextChunk):
        tokens = chunk.text.lower().split() # Normalize text so casing does not play a major role. Split on per word, since most queries are based on a per-word basis, not sentence level.
        for token in tokens:
            if token not in self.index:
                self.index[token] = set() # Store unique Ids.
            self.index[token].add((library_id, doc_id, chunk.id)) # Add doc and chunk id to index. Will update if I think library is worth storing as well.

    def search(self, term: str) -> List[Tuple[str, str, str]]:
        return list(self.index.get(term.lower(), [])) # Gets all document and chunk ids associated with a token.
    
    def delete_chunk(self, term : str, chunk_id : str) -> bool:
        try:
            if term.lower() not in self.index: return False
            # Remove doc id from our set.
            for _, doc_id, cid in self.index[term.lower()]:
                if cid == chunk_id:
                    if doc_id in self.docs: self.docs.remove(doc_id)
                    break
            self.index[term.lower()] = [(lib, doc_id, cid) for lib, doc_id, cid in self.index[term.lower()] if cid != chunk_id]
            return True
        except Exception:
            print (f"Error occurred when trying to delete chunk: {traceback.extract_stack()}")
            return False
    
    def delete_library(self, term : str, library_id : str) -> bool:
        try:
            # Remove doc id from our set.
            for lib, doc_id, _ in self.index[term.lower()]:
                if lib == library_id:
                    self.docs.remove(doc_id)
                    break

            self.index[term.lower()] = [(lib, doc_id, cid) for lib, doc_id, cid in self.index[term.lower()] if lib != library_id]
            return True
        except Exception:
            print (f"Error occurred when trying to delete library: {traceback.extract_stack()}")
            return False
        
