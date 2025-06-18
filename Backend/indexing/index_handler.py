from Backend.indexing.inverted_index import InvertedIndex
from Backend.indexing.lsh_index import LSHIndex
from Backend.utils.embedder import BaseEmbedder

from Common.schemas.library import Library

class IndexHandler():
    def __init__(self, embedder : BaseEmbedder):
        self.inverted = InvertedIndex()
        self.lsh = LSHIndex()
        self.embedder = embedder

    def index_library(self, library: Library):
        for document in library.documents:
            doc_id = document.metadata.id
            for chunk in document.chunks:
                # Add to inverted index (text search)
                self.inverted.add_chunk(doc_id, chunk)

                # Add to vector index (exact vector search)
                self.lsh.add_chunk(doc_id, chunk)

    def do_lsh_search(self, query : str):
        return self.lsh.query_bucket(self.embedder.embed(query))
    
    def do_inverted_search(self, query : str):
        return self.inverted.search(query)