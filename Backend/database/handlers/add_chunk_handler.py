from typing import List, Union

from Backend.database.database_obj import DB

class AddChunkHandler():
    def __init__(self, db : DB):
        self.db = db
    
    def handle_add_chunks(self, chunks : List[Union[str, str, str, bytes, str]]):
        self.db.execute_proc("pr_batch_insert_chunks.sql", chunks)