from typing import List, Union
from database.database_obj import DB
from Common.schemas.library import Library

class AddLibraryHandler():
    def __init__(self, db : DB):
        self.db = db
    
    def handle_add_libraries(self, libraries : List[Union[str, str]]):
        self.db.execute_proc("pr_batch_insert_libraries.sql", libraries)