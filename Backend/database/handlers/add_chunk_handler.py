from typing import Dict, List
import pickle

from database.database_obj import DB
from utils.embedder import SentenceTransformerEmbedder

from Common.schemas.text_chunk import TextChunk

class AddChunkHandler():
    def __init__(self, db : DB):
        self.db = db
    
    def handle_add_chunks(self, embedder : SentenceTransformerEmbedder, chunks : Dict[str, List[TextChunk]]):
        insert_data = []
        for doc_id, chunk_list in chunks.items():
            for chunk in chunk_list:
                chunk.embeddings = embedder.embed(chunk.text)
                insert_data.append((chunk.id, doc_id, chunk.text, pickle.dumps(chunk.embeddings), str(chunk.metadata)))

        self.db.execute_proc("pr_batch_insert_chunks.sql", insert_data)