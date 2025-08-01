-- no_null_messages.sql

SELECT *
FROM {{ ref('stg_telegram_messages') }}
WHERE message IS NULL
  AND media IS NULL
