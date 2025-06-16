INSERT OR IGNORE INTO libraries (id, metadata)
SELECT
  json_extract(lib.value, '$.id'),
  json_extract(lib.value, '$.metadata')
FROM json_each(:json_payload) AS lib;