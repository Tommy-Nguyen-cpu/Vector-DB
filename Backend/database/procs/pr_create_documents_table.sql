CREATE TABLE IF NOT EXISTS documents (
        id TEXT PRIMARY KEY,
        library_id TEXT NOT NULL,
        title TEXT,
        metadata TEXT,
        FOREIGN KEY(library_id) REFERENCES libraries(id) ON DELETE CASCADE
    )