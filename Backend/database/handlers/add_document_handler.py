from Backend.database.database_obj import DB
from Common.schemas.document import Document

class AddDocumentHandler():
    def __init__(self, library_id : str, db : DB):
        self.db = db
        self.library_id = library_id
    
    def handle_add_document(self, document : Document):
        self.db.execute_proc("pr_batch_insert_documents.sql", [(document.id, self.library_id, str(document.metadata))])