from typing import Dict, List
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
from Backend.utils.commonUtils import get_docid_chunk_dict

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
        
        self.cache[library.id] = library
        self.libraryHandler.handle_add_libraries([(library.id, str(library.metadata))])
        self.documentHandler.handle_add_documents(library.id, library.documents.values())
        self.chunkHandler.handle_add_chunks(self.embedder, get_docid_chunk_dict(library.documents.values()))
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
        new_chunks : Dict[str, List[TextChunk]] = {}
        for doc_id, doc in updated_library.documents.items():
            if doc_id in self.index_handler.lsh.docs:
                updated_docs.append((str(doc.metadata), doc_id))
            else:
                new_docs.append(doc)
            for cid, chunk in doc.chunks.items():
                if not chunk.embeddings:
                    new_chunks.setdefault(doc_id, []).append(chunk)
                else:
                    updated_chunks.append((chunk.text, pickle.dumps(chunk.embeddings), str(chunk.metadata), cid))
        
        # Update cache.
        self.cache[updated_library.id] = updated_library

        # Update vector DB indexing.
        self.index_handler.index_library(updated_library)

        # Update DB.
        self.db.execute_proc("pr_batch_update_libraries.sql", [(str(updated_library.metadata), updated_library.id)])
        if updated_docs:
            self.db.execute_proc("pr_batch_update_documents.sql", updated_docs)
        if new_docs:
            self.documentHandler.handle_add_documents(updated_library.id, new_docs)
        if updated_chunks:
            self.db.execute_proc("pr_batch_update_chunks.sql", updated_chunks)
        if new_chunks:
            self.chunkHandler.handle_add_chunks(self.embedder, new_chunks)
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

        # Update vector DB index. We don't want chunks removed to be included in indexing.
        self.index_handler.delete_library(self.cache[library_id])

        # Update cache.
        del self.cache[library_id]

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
                self.chunkHandler.handle_add_chunks(self.embedder, {document_id : [chunk]})
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
    
    #region Test Code
    def test_insert(self):
        library = Library(metadata={"name" : ""})
        for i in range(10):
            document = Document(metadata={})
            for n in range(20):
                chunk = TextChunk(metadata={})
                chunk.text = f"{i}{n}"
                document.chunks[chunk.id] = chunk
            library.documents[document.id] = document
        self.add_new_library(library)

        print("Before deleting.")
        for ids in self.index_handler.lsh.buckets.values():
            print(f"Size: {len(ids)}")
        
        print(f"Chunks: {len(self.db.fetch('SELECT * FROM chunks;'))}")
        print(f"Library: {len(self.db.fetch('SELECT * FROM libraries;'))}")
        print(f"Documents: {len(self.db.fetch('SELECT * FROM documents;'))}")
        
        newDoc = Document(metadata={})
        library.documents[newDoc.id] = newDoc

        self.add_chunk(library.id, newDoc.id, TextChunk(metadata={}, text="Testing"))
        print(f"Received chunks: {len(self.get_chunks(library.id))}")
        print(f"Querying...: {self.search_chunk_from_text(QueryRequest(query = "11", top_k = 5))}")
        print(f"Received library: {self.get_library(library.id)}")
        self.update_library(library)
        self.delete_library(library.id)

        print("after deleting.")
        for ids in self.index_handler.lsh.buckets.values():
            print(f"Size: {len(ids)}")
        print(f"Chunks: {len(self.db.fetch('SELECT * FROM chunks;'))}")
        print(f"Library: {len(self.db.fetch('SELECT * FROM libraries;'))}")
        print(f"Documents: {len(self.db.fetch('SELECT * FROM documents;'))}")
    #endregion