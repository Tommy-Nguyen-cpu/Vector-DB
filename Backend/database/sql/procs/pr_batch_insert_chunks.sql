-- batch_insert_chunks.sql

-- Expects one named parameter: :json_payload

INSERT INTO chunks (id, document_id, text, embedding, metadata)
SELECT
  json_extract(item.value, '$.id'),
  json_extract(item.value, '$.document_id'),
  json_extract(item.value, '$.text'),
  blob(hex(json_extract(item.value, '$.embedding_hex'))),
  json_extract(item.value, '$.metadata')
FROM json_each(:json_payload, '$.chunks') AS item;
