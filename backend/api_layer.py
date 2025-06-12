from fastapi import FastAPI, HTTPException, Path
from pydantic import BaseModel, Field
from typing import List, Dict
from uuid import uuid4

from schemas.text_chunk import TextChunk
from schemas.document import Document
from schemas.library import Library
from utils.mathUtils import cosine_similarity

app = FastAPI()

# --- In-memory storage ---

libraries: Dict[str, Library] = {}

# --- API Routes ---

@app.post("/libraries", response_model=Library)
def create_library(library: Library):
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

@app.post("/libraries/{library_id}/chunks", response_model=TextChunk)
def add_chunk_to_library(library_id: str, chunk: TextChunk):
    library = libraries.get(library_id)
    if not library:
        raise HTTPException(status_code=404, detail="Library not found")

    # For simplicity, we add the chunk to the first document (real logic may vary)
    if not library.documents:
        raise HTTPException(status_code=400, detail="No documents in library to add chunk to")
    
    # TODO: Replace logic with real logic here.
    library.documents[0].chunks.append(chunk)
    return chunk

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

@app.post("/libraries/{library_id}/search", response_model=List[SimilarChunk])
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

    query_embedding = embed_text(request.query)

    similarities = [
        (chunk, cosine_similarity(query_embedding, chunk.embedding))
        for chunk in all_chunks
    ]

    top_chunks = sorted(similarities, key=lambda x: x[1], reverse=True)[:request.top_k]

    return [{"chunk": chunk, "similarity": sim} for chunk, sim in top_chunks]

