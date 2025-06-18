from fastapi import FastAPI, HTTPException, Path, Body
from typing import List, Dict

from Common.schemas.text_chunk import TextChunk
from Common.schemas.document import Document
from Common.schemas.library import Library
from .utils.mathUtils import cosine_similarity
from .utils.embedder import SentenceTransformerEmbedder
from .database.database_obj import DB

from Backend.database.handlers.add_chunk_handler import AddChunkHandler
from Backend.database.handlers.add_document_handler import AddDocumentHandler
from Backend.database.handlers.add_library_handler import AddLibraryHandler

from Backend.indexing.index_handler import IndexHandler

from .api_requests.query_request import QueryRequest

app = FastAPI()

# --- Models ---

embedder = SentenceTransformerEmbedder()

# --- In-memory storage ---

libraries: Dict[str, Library] = {}
index_handler : IndexHandler = IndexHandler(embedder)

# --- DB objects ---

db = DB()

# --- API Routes ---

@app.post("/libraries", response_model=Library)
def create_library(library: Library):
    print(f"Added new library with name {library.metadata["name"]}")
    libraries[library.id] = library
    libraryHandler = AddLibraryHandler(db)
    libraryHandler.handle_add_library(library)
    index_handler.index_library(library)
    return library

@app.get("/libraries/{library_id}", response_model=Library)
def get_library(library_id: str = Path(..., description="ID of the library to retrieve")):
    if library_id not in libraries:
        raise HTTPException(status_code=404, detail="Library not found")
    return libraries[library_id]

# Most of the updating can actually be performed in here, but that might not be what is required.
@app.put("/libraries/{library_id}", response_model=Library)
def update_library(library_id: str, updated_library: Library):
    if library_id not in libraries:
        raise HTTPException(status_code=404, detail="Library not found")
    libraries[library_id] = updated_library
    index_handler.index_library(library)
    return updated_library

@app.delete("/libraries/{library_id}")
def delete_library(library_id: str):
    if library_id not in libraries:
        raise HTTPException(status_code=404, detail="Library not found")
    del libraries[library_id]
    return {"detail": "Library deleted"}

@app.post("/libraries/{library_id}/{document_id}/chunks", response_model=bool)
def add_chunk_to_library(library_id: str, document_id : str, chunk: TextChunk):
    chunk.embeddings = embedder.embed(chunk.text) # Embed the text for ease of use later on.

    library = libraries.get(library_id)
    if not library:
        raise HTTPException(status_code=404, detail="Library not found")

    if not library.documents:
        raise HTTPException(status_code=400, detail="No documents in library to add chunk to")
    
    index_handler.index_library(library)
    for document in library.documents:
        if document_id == document.id:
            document.chunks.append(chunk)
            chunkHandler = AddChunkHandler(library.id, document.id, db)
            chunkHandler.handle_add_chunk(chunk)
            return True
    
    return False

@app.delete("/libraries/{library_id}/chunks/{chunk_id}")
def delete_chunk_from_library(library_id: str, chunk_id: str):
    library = libraries.get(library_id)
    if not library:
        raise HTTPException(status_code=404, detail="Library not found")

    found = False
    for _, doc in library.documents.items():
        if chunk_id in doc.chunks:
            del doc.chunks[chunk_id]
            found = True
            break

    if not found:
        raise HTTPException(status_code=404, detail="Chunk not found")

    return {"detail": "Chunk deleted"}

@app.post("/libraries/{library_id}/search", response_model=List[TextChunk])
def search_chunks_from_text(
    library_id: str,
    request: QueryRequest = Body(...)
):
    library = libraries.get(library_id)
    if not library:
        raise HTTPException(status_code=404, detail="Library not found")
    
    ids = index_handler.do_lsh_search(request.query)

    if not ids:
        raise HTTPException(status_code=400, detail="No chunks available in library")

    query_embedding = embedder.embed(request.query)

    similarities = [
        (chunk, cosine_similarity(query_embedding, library.documents[doc_id].chunks[chunk_id].embedding))
        for doc_id, chunk_id in ids
    ]

    top_chunks = sorted(similarities, key=lambda x: x[1], reverse=True)[:request.top_k]

    return [{"chunk": chunk, "similarity": sim} for chunk, sim in top_chunks]

if __name__ == '__main__':
    

    library = Library(metadata={"name" : ""})
    for i in range(10):
        document = Document(metadata={})
        for n in range(20):
            chunk = TextChunk(metadata={})
            chunk.text = f"{i}{n}"
    create_library(library)

    request = QueryRequest(query = "12", top_k = 5)
    result = search_chunks_from_text(library.id, request=request)
    print(f"Final: {result}")

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