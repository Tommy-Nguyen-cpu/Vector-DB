from typing import List
from Backend.database.database_obj import DB

from Common.schemas.document import Document

class AddDocumentHandler():
    def __init__(self, db : DB):
        self.db = db
    
    def handle_add_documents(self, library_id : str, documents : List[Document]):
        docs = []
        for doc in documents:
            docs.append((doc.id, library_id, str(doc.metadata)))

        self.db.execute_proc("pr_batch_insert_documents.sql", docs)