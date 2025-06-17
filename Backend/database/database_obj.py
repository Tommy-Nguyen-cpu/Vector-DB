import sqlite3
import os
from pathlib import Path

class DB():
    # Get the directory where this script lives
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    def __init__(self, vector_db_file = "vector_db.sqlite"):
        self.conn = sqlite3.connect(vector_db_file)

        # For now, we will create the tables upon server start up.
        self.execute_sql_file(DB.construct_sql_path("sql/startup", "create_libraries_table.sql"))
        self.execute_sql_file(DB.construct_sql_path("sql/startup", "create_documents_table.sql"))
        self.execute_sql_file(DB.construct_sql_path("sql/startup", "create_chunks_table.sql"))
    
    def execute_sql_file(self, file_path: str):
        if not self.is_connection_open():
            return
        
        with open(file_path, "r") as f:
            sql_script = f.read()
        self.conn.executescript(sql_script)
        self.conn.commit()
    
    def execute_proc(self, file_name : str, objects):
        proc_path = DB.construct_sql_path("sql/procs", file_name)

        sql = Path(proc_path).read_text()
        self.conn.executemany(sql, objects)
        self.conn.commit()
    
    def fetch(self, sql_line : str):
        return self.conn.execute(sql_line).fetchall()
    
    def is_connection_open(self):
        '''
        Verifies if the connection is open by attempting to run a single SQL line.
        '''
        try:
            self.conn.execute("SELECT 1")
            return True
        except sqlite3.ProgrammingError:
            return False
        
    def close_connection(self):
        self.conn.close()
    
    def construct_sql_path(folder : str, file_name : str):
        return os.path.join(DB.BASE_DIR, folder, file_name)
