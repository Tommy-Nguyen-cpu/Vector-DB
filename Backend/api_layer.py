from fastapi import FastAPI, Path, Body
from typing import List, Dict, Union
import traceback

from Common.schemas.text_chunk import TextChunk
from Common.schemas.library import Library

from data.library_data_manager import LibraryDataManager

from Common.api_requests.query_request import QueryRequest

app = FastAPI()

# Data Managers
library_manager = LibraryDataManager()

# --- API Routes ---

@app.post("/libraries", response_model=Library)
def create_library(library: Library):
    print(f"Added new library with name {library.metadata["name"]}")
    return library_manager.add_new_library(library)

@app.get("/libraries/{library_id}", response_model=Library)
def get_library_by_id(library_id: str = Path(..., description="ID of the library to retrieve")):
    return library_manager.get_library(library_id)

@app.get("/libraries", response_model=List[Library])
def get_library():
    return library_manager.get_all_libraries()

@app.put("/libraries/{library_id}", response_model=Library)
def update_library(updated_library: Library):
    return library_manager.update_library(updated_library)

@app.delete("/libraries/{library_id}", response_model=Dict[str, str])
def delete_library(library_id: str):
    return library_manager.delete_library(library_id)

@app.post("/libraries/{library_id}/{document_id}/chunks", response_model=bool)
def add_chunk_to_library(library_id: str, document_id : str, chunk: TextChunk):
    return library_manager.add_chunk(library_id, document_id, chunk)

@app.put("/libraries/{library_id}/{document_id}/chunks/{chunk_id}", response_model=bool)
def update_chunk(library_id : str, document_id : str, chunk_id : str, chunk :TextChunk):
    try:
        library_manager.update_chunk(library_id, document_id, chunk_id, chunk)
        return True
    except:
        print(f"API failed with exception: {traceback.extract_stack()}")
        return False

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
    library_manager.test_insert()