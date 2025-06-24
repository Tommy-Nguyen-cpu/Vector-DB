import streamlit as st
import requests
from typing import List, Union, Dict

import sys
from pathlib import Path

from Common.schemas.library import Library
from Common.schemas.document import Document
from Common.schemas.text_chunk import TextChunk
from Common.api_requests.query_request import QueryRequest

# API Url
api_url = "http://127.0.0.1:8000"

# Pydantic-like schemas for input serialization
# These are simple dicts in this UI

# REST helpers returning Pydantic models
API_TIMEOUT = 5
BASE_HEADERS = {"Content-Type": "application/json"}
# REST helpers

# REST helpers

def fetch_libraries(api_url: str) -> List[Library]:
    resp = requests.get(f"{api_url}/libraries", timeout=API_TIMEOUT)
    resp.raise_for_status()
    return [Library.parse_obj(d) for d in resp.json()]

def fetch_library(lib_id: str, api_url: str) -> Library:
    resp = requests.get(f"{api_url}/libraries/{lib_id}", timeout=API_TIMEOUT)
    resp.raise_for_status()
    return Library.parse_obj(resp.json())

def create_library(api_url: str, lib: Library) -> Library:
    resp = requests.post(f"{api_url}/libraries", json=lib.dict(), headers=BASE_HEADERS, timeout=API_TIMEOUT)
    resp.raise_for_status()
    return Library.parse_obj(resp.json())


def update_library(api_url: str, lib: Library) -> Library:
    resp = requests.put(f"{api_url}/libraries/{lib.id}", json=lib.dict(), headers=BASE_HEADERS, timeout=API_TIMEOUT)
    resp.raise_for_status()
    return Library.parse_obj(resp.json())


def delete_library(api_url: str, lib_id: str):
    resp = requests.delete(f"{api_url}/libraries/{lib_id}", timeout=API_TIMEOUT)
    resp.raise_for_status()
    return resp.json()


def add_chunk(api_url: str, lib_id: str, doc_id: str, text: str) -> TextChunk:
    payload = TextChunk(text = text, metadata={})
    resp = requests.post(f"{api_url}/libraries/{lib_id}/{doc_id}/chunks", payload.json(), timeout=API_TIMEOUT)
    resp.raise_for_status()


def update_chunk(api_url: str, lib_id: str, doc_id: str, chunk: TextChunk) -> TextChunk:
    resp = requests.put(
        f"{api_url}/libraries/{lib_id}/{doc_id}/chunks/{chunk.id}", json=chunk.dict(), timeout=API_TIMEOUT
    )
    resp.raise_for_status()
    if resp.json() is not True:
        print("API failed when updating chunk.")


def delete_chunk(api_url: str, lib_id: str, chunk_id: str):
    resp = requests.delete(f"{api_url}/libraries/{lib_id}/chunks/{chunk_id}", timeout=API_TIMEOUT)
    resp.raise_for_status()
    return resp.json()

# Streamlit UI
st.set_page_config(page_title="Library Manager", layout="wide")
st.title("📚 Library Manager")

# API URL input
api_url = st.text_input("API Base URL", value="http://localhost:8000")

# Sidebar: Create new library
with st.sidebar.expander("➕ Create New Library", expanded=True):
    new_lib_name = st.text_input("Library Name", key="new_lib_name")
    if st.button("Create Library"):
        lib = Library(metadata={"name": new_lib_name}, documents={})
        try:
            create_library(api_url, lib)
            st.success("Library created successfully!")
            st.rerun()
        except Exception as e:
            st.error(f"Failed to create library: {e}")

# Refresh
if st.button("🔄 Refresh Libraries"):
    st.rerun()

# Fetch libraries
try:
    libraries = fetch_libraries(api_url)
except Exception as e:
    st.error(f"Could not fetch libraries: {e}")
    libraries = []

# Display each library
for lib in libraries:
    with st.expander(f"Library: {lib.metadata.get('name')} (ID: {lib.id})", expanded=False):
        # Library controls
        col1, col2 = st.columns([3,1])
        lib_name = col1.text_input("Library Name", value=lib.metadata.get('name',''), key=f"lib_name_{lib.id}")
        if col1.button("Save Library", key=f"save_lib_{lib.id}"):
            try:
                lib.metadata['name'] = lib_name
                update_library(api_url, lib)
                st.success("Library updated")
                st.rerun()
            except Exception as e:
                st.error(f"Error saving library: {e}")
        if col2.button("Delete Library", key=f"del_lib_{lib.id}"):
            try:
                delete_library(api_url, lib.id)
                st.success("Library deleted")
                st.rerun()
            except Exception as e:
                st.error(f"Error deleting library: {e}")

        st.markdown("---")
        # Add Document section
        st.subheader("➕ Add Document")
        new_doc_name = st.text_input("Document Name", key=f"new_doc_name_{lib.id}")
        if st.button("Add Document", key=f"add_doc_{lib.id}"):
            # Append empty chunks
            doc = Document(metadata={"name": new_doc_name}, chunks={})
            lib.documents[doc.id] = doc
            try:
                update_library(api_url, lib)
                st.success("Document added")
                st.rerun()
            except Exception as e:
                st.error(f"Error adding document: {e}")

        # List documents
        for doc in lib.documents.values():
            with st.container():
                st.markdown(f"### Document: {doc.metadata.get('name')} (ID: {doc.id})")
                # Add Chunk for this document
                new_chunk = st.text_input("New Chunk Text", key=f"new_chunk_text_{doc.id}")
                if st.button("Add Chunk", key=f"add_chunk_{doc.id}"):
                    try:
                        add_chunk(api_url, lib.id, doc.id, new_chunk)
                        st.success("Chunk added")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error adding chunk: {e}")

                # List chunks
                for chunk in doc.chunks.values():
                    txt = st.text_area("Chunk Text", value=chunk.text, key=f"chunk_{chunk.id}")
                    c1, c2 = st.columns(2)
                    if c1.button("Save Chunk", key=f"save_chunk_{chunk.id}"):
                        try:
                            chunk.text = st.session_state[f"chunk_{chunk.id}"]
                            update_chunk(api_url, lib.id, doc.id, chunk)
                            st.success("Chunk updated")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error updating chunk: {e}")
                    if c2.button("Delete Chunk", key=f"del_chunk_{chunk.id}"):
                        try:
                            delete_chunk(api_url, lib.id, chunk.id)
                            st.success("Chunk deleted")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error deleting chunk: {e}")
                st.markdown("---")

st.sidebar.header("Fetch Library by ID")
fetch_id = st.sidebar.text_input("Library ID", key="fetch_id")
if st.sidebar.button("Fetch Library"):
    try:
        lib = fetch_library(fetch_id, api_url)
    except Exception as e:
        st.sidebar.error(f"Failed to fetch: {e}")
        st.stop()

    # --- TOP LEVEL: one tab per library (just one here) ---
    tabs = st.tabs([f"{lib.metadata.get('name', lib.id)}"])
    lib_tab = tabs[0]

    with lib_tab:
        st.markdown(f"**Library ID:** {lib.id}")
        st.json(lib.metadata)

        # --- SECOND LEVEL: one expander per document ---
        for doc in lib.documents.values():
            with st.expander(f"Document: {doc.metadata.get('title', doc.id)}"):
                st.markdown(f"- **Doc ID:** {doc.id}")
                st.json(doc.metadata)

                # --- INLINE chunk list (no further expanders!) ---
                st.markdown("**Chunks**")
                for chunk in doc.chunks.values():
                    st.text_area(
                        label=f"Chunk {chunk.id[:8]} text", 
                        value=chunk.text, 
                        key=f"text_{chunk.id}"
                    )

st.header("🔍 Search Chunks by Text")

with st.form("search_form"):
    query_text = st.text_input("Search query", key="query_text")
    top_k = st.number_input("Top K results", min_value=1, max_value=50, value=5, step=1)
    submitted = st.form_submit_button("Search")

if submitted:
    payload = {
        "query": query_text,
        "top_k": top_k
    }

    try:
        resp = requests.post(f"{api_url}/libraries/search", json=payload, timeout=5)
        resp.raise_for_status()
        raw_results: List[Dict[str, Union[dict, float]]] = resp.json()

        st.success(f"Found {len(raw_results)} results")

        for idx, result in enumerate(raw_results):
            chunk_data = result["0"] if "0" in result else result.get("text_chunk", result.get("chunk", None))
            score = result.get("1") if "1" in result else result.get("similarity", None)

            try:
                chunk = TextChunk.parse_obj(chunk_data)
            except Exception:
                st.warning(f"Could not parse chunk: {chunk_data}")
                continue

            with st.expander(f"Result {idx+1} - Score: {score:.4f}" if score is not None else f"Result {idx+1}"):
                st.markdown("**Chunk Text**")
                st.code(chunk.text, language="markdown")
                st.markdown("**Metadata**")
                st.json(chunk.metadata)
                st.markdown("**Embeddings**")
                st.write(chunk.embeddings[:10])  # optionally show top N dims only

    except requests.exceptions.HTTPError as e:
        try:
            detail = resp.json()
        except ValueError:
            detail = resp.text
        st.error(f"HTTP error {resp.status_code}: {detail}")
    except Exception as e:
        st.error(f"Unexpected error: {e}")