import gradio as gr

from Common.schemas.library import Library
from Common.schemas.document import Document
from Common.schemas.text_chunk import TextChunk

# Internal state
documents : dict[str, Document] = {}
global_libraries : dict[str, Library] = {}

with gr.Blocks() as demo:
    # State tracking library→docs→chunks
    state = gr.State({})
    
    lib_name = gr.TextArea(label = "New library name.")
    new_lib_btn = gr.Button("Add Library")

    # Dynamically render everything based on state
    @gr.render(inputs=[lib_name, state])
    def render_hierarchy(curr_lib_name, libraries):
        # Add a button for each library
        for lib_id, docs in libraries.items():
            gr.Markdown(f"## Library: `{curr_lib_name}`")
            doc_name = gr.TextArea(label = "New document name.")
            lib_add_doc = gr.Button("Add Document", elem_id=f"add_doc_{lib_id}")
            
            # When clicked, trigger a change to state
            @lib_add_doc.click(inputs=[doc_name, state], outputs=[state])
            def _add_doc(name, libs, lib_id=lib_id):
                doc = Document(metadata={"name" : name})
                documents[doc.id] = doc
                global_libraries[lib_id].documents.append(doc)
                libs[lib_id].append({doc.id: [doc]})
                return libs

            # For each document, render its UI
            for doc in docs:
                for doc_id, chunks in doc.items():
                    gr.Markdown(f"### Document `{doc_name.value}`")
                    chunk_name = gr.TextArea(label = "New chunk name.")
                    doc_add_chunk = gr.Button("Add Chunk", elem_id=f"add_chunk_{doc_id}")

                    @doc_add_chunk.click(inputs=[chunk_name, state], outputs=[state])
                    def _add_chunk(name, libs, doc_id=doc_id):
                        chunk = TextChunk(metadata={"name" : name})
                        documents[doc.id].chunks.append(chunk)
                        for lib_docs in libs.values():
                            for d in lib_docs:
                                if doc_id in d:
                                    d[doc_id].append(chunk)
                        return libs

                    # Render existing chunks
                    for idx, _ in enumerate(chunks):
                        gr.Textbox(label=f"Chunk {idx+1}", lines=2)

    save_btn = gr.Button("Save All")
    output = gr.Textbox()

    @new_lib_btn.click(inputs=[lib_name, state], outputs=[state])
    def add_library(name, libs):
        library = Library(metadata = {"name" : name})
        global_libraries[library.id] = library
        libs[str(library.id)] = []
        return libs

    @save_btn.click(inputs=[state], outputs=[output])
    def save_all(libraries):
        total = sum(len(docs) for docs in libraries.values())
        return f"Saving {len(libraries)} libraries and {total} documents."

demo.launch()
