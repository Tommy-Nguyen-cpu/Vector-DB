-- Batch inserts a set of chunks into db, with document id.

INSERT INTO chunks (id, document_id, text, embedding, metadata) VALUES (?, ?, ?, ?, ?);
