CREATE TABLE IF NOT EXISTS documents (
        id TEXT PRIMARY KEY,
        library_id TEXT NOT NULL,
        metadata TEXT,
        FOREIGN KEY(library_id) REFERENCES libraries(id) ON DELETE CASCADE
    )