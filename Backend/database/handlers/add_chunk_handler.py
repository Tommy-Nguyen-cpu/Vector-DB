import pickle

from Backend.database.database_obj import DB
from Common.schemas.text_chunk import TextChunk

class AddChunkHandler():
    def __init__(self, library_id : str, document_id : str, db : DB):
        self.library_id = library_id
        self.document_id = document_id
        self.db = db
    
    def handle_add_chunk(self, chunk : TextChunk):
        self.db.execute_proc("pr_batch_insert_chunks.sql", [(chunk.id, self.document_id, chunk.text, pickle.dumps(chunk.embeddings), str(chunk.metadata))])