from typing import Dict
from fastapi import HTTPException
import pickle

from Backend.database.database_obj import DB
from Backend.database.handlers.add_library_handler import AddLibraryHandler
from Backend.database.handlers.add_document_handler import AddDocumentHandler
from Backend.database.handlers.add_chunk_handler import AddChunkHandler

from Backend.api_requests.query_request import QueryRequest

from Backend.indexing.index_handler import IndexHandler
from Backend.utils.embedder import SentenceTransformerEmbedder
from Backend.utils.mathUtils import cosine_similarity

from Common.schemas.library import Library
from Common.schemas.document import Document
from Common.schemas.text_chunk import TextChunk

class LibraryDataManager:
    _instance = None
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance
    
    def __init__(self):
        self.cache : Dict[str, Library] = {}

        # DB & DB interaction handler objects.
        self.db = DB()
        self.libraryHandler = AddLibraryHandler(self.db)
        self.documentHandler = AddDocumentHandler(self.db)
        self.chunkHandler = AddChunkHandler(self.db)

        # Embedding & vector DB indexing handler.
        self.embedder = SentenceTransformerEmbedder()
        self.index_handler : IndexHandler = IndexHandler(self.embedder)
    
    #region Library Methods
    def add_new_library(self, library : Library):
        if library.id in self.cache:
            HTTPException(status_code=404, detail="Attempted to add a library that already exists!")

        docs = []
        chunks = []
        for doc in library.documents.values():
            docs.append((doc.id, library.id, str(doc.metadata)))
            for chunk in doc.chunks.values():
                chunk.embeddings = self.embedder.embed(chunk.text) # Embed the text for ease of use later on.
                chunks.append((chunk.id, doc.id, chunk.text, pickle.dumps(chunk.embeddings), str(chunk.metadata)))
        
        self.cache[library.id] = library
        self.libraryHandler.handle_add_libraries([(library.id, str(library.metadata))])
        self.documentHandler.handle_add_documents(docs)
        self.chunkHandler.handle_add_chunks(chunks)
        self.index_handler.index_library(library)
        return library
    
    def get_library(self, library_id : str):
        if library_id not in self.cache:
            raise HTTPException(status_code=404, detail="Library not found")
        return self.cache[library_id]
    
    def update_library(self, updated_library : Library):
        if updated_library.id not in self.cache:
                raise HTTPException(status_code=404, detail="Library not found")
        
        # Form the data we will be inserting into DB. Might be better to simplify this and have it be returned in a utils method.
        updated_docs = []
        new_docs = []
        updated_chunks = []
        new_chunks = []
        for doc_id, doc in updated_library.documents.items():
            if doc_id in self.index_handler.lsh.docs:
                updated_docs.append((doc.metadata, doc_id))
            else:
                new_docs.append((doc.id, updated_library.id, str(doc.metadata)))
            for cid, chunk in doc.chunks.items():
                if not chunk.embeddings:
                    new_chunks.append((cid, doc.id, chunk.text, pickle.dumps(chunk.embeddings), str(chunk.metadata)))
                else:
                    updated_chunks.append((chunk.text, pickle.dumps(chunk.embeddings), str(chunk.metadata), cid))
        
        # Update cache.
        self.cache[updated_library.id] = updated_library

        # Update vector DB indexing.
        self.index_handler.index_library(updated_library)

        # Update DB.
        self.db.execute_proc("pr_batch_update_libraries.sql", [(updated_library.metadata, updated_library.id)])
        if updated_docs:
            self.db.execute_proc("pr_batch_update_documents.sql", updated_docs)
        if new_docs:
            self.documentHandler.handle_add_documents(new_docs)
        if updated_chunks:
            self.db.execute_proc("pr_batch_update_chunks.sql", updated_chunks)
        if new_chunks:
            self.chunkHandler.handle_add_chunks(new_chunks)
        return updated_library
    
    def delete_library(self, library_id : str):
        if library_id not in self.cache:
                raise HTTPException(status_code=404, detail="Library not found")

        doc_ids = []
        chunk_ids = []
        for doc_id, doc in self.cache[library_id].documents.items():
            doc_ids.append((doc_id,))
            for chunk_id in doc.chunks.keys():
                chunk_ids.append((chunk_id,))
        
        # Update cache.
        del self.cache[library_id]

        # Update vector DB index. We don't want chunks removed to be included in indexing.
        self.index_handler.delete_library(self.cache[library_id])

        # Update DB. Delete chunks, then documents, and lastly library to avoid dependency issues.
        self.db.execute_proc("pr_batch_delete_chunks.sql", chunk_ids)
        self.db.execute_proc("pr_batch_delete_documents.sql", doc_ids)
        self.db.execute_proc("pr_batch_delete_libraries.sql", [(library_id, )])

        return {"detail": "Library deleted"}
    #endregion


    #region Chunk Methods
    def add_chunk(self, library_id : str, document_id : str, chunk : TextChunk):
        chunk.embeddings = self.embedder.embed(chunk.text) # Embed the text for ease of use later on.

        library = self.cache.get(library_id)
        if not library:
            raise HTTPException(status_code=404, detail="Library not found")

        if not library.documents:
            raise HTTPException(status_code=400, detail="No documents in library to add chunk to")
        
        self.index_handler.index_library(library)
        for _, document in library.documents.items():
            if document_id == document.id:
                document.chunks.setdefault(chunk.id, chunk)
                self.chunkHandler.handle_add_chunks([(chunk.id, document_id, chunk.text, chunk.embeddings, str(chunk.metadata))])
                return True
        
        return False
    
    def delete_chunk(self, library_id : str, chunk_id : str):
        library = self.cache.get(library_id)
        if not library:
            raise HTTPException(status_code=404, detail="Library not found")

        found = False

        self.db.execute_proc("pr_batch_delete_chunks.sql", [(chunk_id,)])
        for _, doc in library.documents.items():
            if chunk_id in doc.chunks:
                self.index_handler.delete_chunk(doc.chunks[chunk_id])
                del doc.chunks[chunk_id]
                found = True
                break

        if not found:
            raise HTTPException(status_code=404, detail="Chunk not found")

        return {"detail": "Chunk deleted"}
    
    def get_chunks(self, library_id : str):
        chunks = []

        library = self.cache.get(library_id)
        for _, doc in library.documents.items():
            for _, chunk in doc.chunks.items():
                chunks.append(chunk)
        
        return chunks
    #endregion
    
    def search_chunk_from_text(self, request : QueryRequest):
        ids = self.index_handler.do_lsh_search(request.query)

        if not ids:
            raise HTTPException(status_code=400, detail="No chunks available in library")

        query_embedding = self.embedder.embed(request.query)

        similarities = [
            (self.cache[library_id].documents[doc_id].chunks[chunk_id], cosine_similarity(query_embedding, self.cache[library_id].documents[doc_id].chunks[chunk_id].embeddings))
            for library_id, doc_id, chunk_id in ids
        ]

        top_chunks = sorted(similarities, key=lambda x: x[1], reverse=True)[:request.top_k]

        return [{"chunk": chunk, "similarity": sim} for chunk, sim in top_chunks]