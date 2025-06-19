-- Batch inserts libraries into libraries database table.
UPDATE documents
SET metadata = ?
WHERE id = ?;