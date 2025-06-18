import pickle

from Backend.database.database_obj import DB
from Common.schemas.text_chunk import TextChunk

class AddChunkHandler():
    def __init__(self, db : DB):
        self.db = db
    
    def handle_add_chunk(self, document_id : str, chunk : TextChunk):
        self.db.execute_proc("pr_batch_insert_chunks.sql", [(chunk.id, document_id, chunk.text, pickle.dumps(chunk.embeddings), str(chunk.metadata))])