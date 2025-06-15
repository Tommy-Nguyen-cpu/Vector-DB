from fastapi import FastAPI, HTTPException, Path, Body
from typing import List, Dict

from Common.schemas.text_chunk import TextChunk
from Common.schemas.document import Document
from Common.schemas.library import Library
from .utils.mathUtils import cosine_similarity
from .utils.embedder import SentenceTransformerEmbedder

from .api_requests.query_request import QueryRequest

app = FastAPI()

# --- In-memory storage ---

libraries: Dict[str, Library] = {}

# --- Models ---

embedder = SentenceTransformerEmbedder()

# --- API Routes ---

@app.post("/libraries", response_model=Library)
def create_library(library: Library):
    print(f"Added new library with name {library.metadata["name"]}")
    libraries[library.id] = library
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
    
    for document in library.documents:
        if document_id == document.id:
            return True
    return False

@app.delete("/libraries/{library_id}/chunks/{chunk_id}")
def delete_chunk_from_library(library_id: str, chunk_id: str):
    library = libraries.get(library_id)
    if not library:
        raise HTTPException(status_code=404, detail="Library not found")

    found = False
    for doc in library.documents:
        for i, chunk in enumerate(doc.chunks):
            if chunk.id == chunk_id:
                del doc.chunks[i]
                found = True
                break
        if found:
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

    all_chunks = []
    for doc in library.documents:
        all_chunks.extend(doc.chunks)

    if not all_chunks:
        raise HTTPException(status_code=400, detail="No chunks available in library")

    query_embedding = embedder.embed(request.query)

    similarities = [
        (chunk, cosine_similarity(query_embedding, chunk.embedding))
        for chunk in all_chunks
    ]

    top_chunks = sorted(similarities, key=lambda x: x[1], reverse=True)[:request.top_k]

    return [{"chunk": chunk, "similarity": sim} for chunk, sim in top_chunks]

# if __name__ == '__main__':
#     print("Initializing model...")
#     print("model initialized.")

#     print("Encoding text...")
#     embeddings = embedder.embed(["testing"])
#     print(f"{embeddings}")