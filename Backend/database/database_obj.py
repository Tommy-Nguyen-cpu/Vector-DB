import sqlite3

class DB():
    def __init__(self, vector_db_file = "vector_db.sqlite"):
        self.conn = sqlite3.connect(vector_db_file)

        # For now, we will create the tables upon server start up.
        self.execute_sql_file("Backend/procs/pr_create_libraries_table.sql")
        self.execute_sql_file("Backend/procs/pr_create_documents_table.sql")
        self.execute_sql_file("Backend/procs/pr_create_chunks_table.sql")
    
    def execute_sql_file(self, file_path: str):
        if not self.is_connection_open():
            return
        
        with open(file_path, "r") as f:
            sql_script = f.read()
        self.conn.executescript(sql_script)
        self.conn.commit()
    
    def is_connection_open(self):
        '''
        Verifies if the connection is open by attempting to run a single SQL line.
        '''
        try:
            self.conn.execute("SELECT 1")
            return True
        except sqlite3.ProgrammingError:
            return False
