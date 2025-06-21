import pickle
from fastapi import FastAPI, HTTPException, Path, Body
from typing import List, Dict, Union

from Common.schemas.text_chunk import TextChunk
from Common.schemas.document import Document
from Common.schemas.library import Library

from Backend.data.library_data_manager import LibraryDataManager

from .api_requests.query_request import QueryRequest

app = FastAPI()

# Data Managers
library_manager = LibraryDataManager()

# --- API Routes ---

@app.post("/libraries", response_model=Library)
def create_library(library: Library):
    print(f"Added new library with name {library.metadata["name"]}")
    return library_manager.add_new_library(library)

@app.get("/libraries/{library_id}", response_model=Library)
def get_library(library_id: str = Path(..., description="ID of the library to retrieve")):
    return library_manager.get_library(library_id)

@app.put("/libraries/{library_id}", response_model=Library)
def update_library(updated_library: Library):
    return library_manager.update_library(updated_library)

@app.delete("/libraries/{library_id}", response_model=Dict[str, str])
def delete_library(library_id: str):
    return library_manager.delete_library(library_id)

@app.post("/libraries/{library_id}/{document_id}/chunks", response_model=bool)
def add_chunk_to_library(library_id: str, document_id : str, chunk: TextChunk):
    return library_manager.add_chunk(library_id, document_id, chunk)

@app.delete("/libraries/{library_id}/chunks/{chunk_id}")
def delete_chunk_from_library(library_id: str, chunk_id: str):
    return library_manager.delete_chunk(library_id, chunk_id)

@app.get("/libraries/{library_id}", response_model = List[TextChunk])
def get_chunks(library_id : str):
    return library_manager.get_chunks(library_id)

@app.post("/libraries/search", response_model=List[Dict[str, Union[TextChunk, float]]])
def search_chunks_from_text(
    request: QueryRequest = Body(...)
) -> List[Dict[str, Union[TextChunk, float]]]:  
    return library_manager.search_chunk_from_text(request)

if __name__ == '__main__':

    library = Library(metadata={"name" : ""})
    for i in range(10):
        document = Document(metadata={})
        for n in range(20):
            chunk = TextChunk(metadata={})
            chunk.text = f"{i}{n}"
            document.chunks[chunk.id] = chunk
        library.documents[document.id] = document
    create_library(library)

    request = QueryRequest(query = "12", top_k = 5)
    result = search_chunks_from_text(request=request)
    # print(f"Final: {result}")

    print("Before deleting.")
    for ids in index_handler.lsh.buckets.values():
        print(f"Size: {len(ids)}")
    
    print(f"Chunks: {len(db.fetch('SELECT * FROM chunks;'))}")
    print(f"Library: {len(db.fetch('SELECT * FROM libraries;'))}")
    print(f"Documents: {len(db.fetch('SELECT * FROM documents;'))}")
    
    delete_library(library.id)

    print("after deleting.")
    for ids in index_handler.lsh.buckets.values():
        print(f"Size: {len(ids)}")
    print(f"Chunks: {len(db.fetch('SELECT * FROM chunks;'))}")
    print(f"Library: {len(db.fetch('SELECT * FROM libraries;'))}")
    print(f"Documents: {len(db.fetch('SELECT * FROM documents;'))}")

    # document = Document(metadata={"name" : ""})
    # chunk = TextChunk(metadata={"name" : ""})

    # libraryHandler = AddLibraryHandler(db)
    # libraryHandler.handle_add_library(library)
    # print(f"Library Insert Result: {db.fetch('SELECT * FROM libraries;')}")

    # documentHandler = AddDocumentHandler(library.id, db)
    # documentHandler.handle_add_document(document)
    # print(f"Document Insert Result: {db.fetch('SELECT * FROM documents;')}")

    # chunkHandler = AddChunkHandler(library.id, document.id, db)
    # chunkHandler.handle_add_chunk(chunk)
    # print(f"Chunk Insert Result: {db.fetch('SELECT * FROM chunks;')}")



    # json = Library(metadata={"name" : ""})
    # print(f"json: {json}")
    # db.execute_proc("pr_batch_insert_libraries.sql", [(json.id, str(json.metadata))])
    # print(f"Result: {db.fetch('SELECT * FROM libraries;')}")