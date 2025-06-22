from typing import List

from Backend.indexing.inverted_index import InvertedIndex
from Backend.indexing.lsh_index import LSHIndex
from Backend.utils.embedder import BaseEmbedder

from Common.schemas.library import Library
from Common.schemas.text_chunk import TextChunk

class IndexHandler():
    def __init__(self, embedder : BaseEmbedder):
        self.inverted = InvertedIndex()
        self.lsh = LSHIndex()
        self.embedder = embedder

    def index_library(self, library: Library):
        for doc_id, document in library.documents.items():
            for _, chunk in document.chunks.items():
                # Add to inverted index (text search)
                self.inverted.add_chunk(library.id, doc_id, chunk)

                # Add to vector index (exact vector search)
                self.lsh.add_chunk(library.id, doc_id, chunk)

    def do_lsh_search(self, query : str):
        return self.lsh.query_bucket(self.embedder.embed(query))
    
    def do_inverted_search(self, query : str):
        return self.inverted.search(query)
    
    def delete_chunk(self, chunk : TextChunk):
        self.lsh.delete_chunk(chunk.id, chunk.embeddings)
        self.inverted.delete_chunk(chunk.text, chunk.id)
    
    def add_chunk(self, library_id : str, document_id : str, chunk : TextChunk):
        self.lsh.add_chunk(library_id, document_id, chunk)
        self.inverted.add_chunk(library_id, document_id, chunk)
    
    def update_chunk(self, library_id : str, document_id : str, chunk : TextChunk):
        self.lsh.delete_chunk(chunk.id, chunk.embeddings)
        self.inverted.delete_chunk(chunk.text, chunk.id)

        self.add_chunk(library_id, document_id, chunk)
    
    # TODO: If we are considering time vs memory, storing the lib and doc ids as a separate hash might be preferred over the for loop.
    def delete_library(self, library : Library):
        for _, doc in library.documents.items():
            for _, chunk in doc.chunks.items():
                self.lsh.delete_library(library.id, chunk.embeddings)
                self.inverted.delete_chunk(chunk.text, chunk.id)