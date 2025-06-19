from typing import List, Union
from Backend.database.database_obj import DB
from Common.schemas.document import Document

class AddDocumentHandler():
    def __init__(self, library_id : str, db : DB):
        self.db = db
        self.library_id = library_id
    
    def handle_add_document(self, documents : List[Union[str, str, str]]):
        self.db.execute_proc("pr_batch_insert_documents.sql", documents)