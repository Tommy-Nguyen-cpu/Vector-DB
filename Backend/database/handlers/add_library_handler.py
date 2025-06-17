from Backend.database.database_obj import DB
from Common.schemas.library import Library

class AddLibraryHandler():
    def __init__(self, db : DB):
        self.db = db
    
    def handle_add_library(self, library : Library):
        self.db.execute_proc("pr_batch_insert_libraries.sql", [(library.id, str(library.metadata))])