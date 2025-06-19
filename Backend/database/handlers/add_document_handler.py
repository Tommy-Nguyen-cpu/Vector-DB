from typing import List, Union
from Backend.database.database_obj import DB

class AddDocumentHandler():
    def __init__(self, db : DB):
        self.db = db
    
    def handle_add_documents(self, documents : List[Union[str, str, str]]):
        self.db.execute_proc("pr_batch_insert_documents.sql", documents)