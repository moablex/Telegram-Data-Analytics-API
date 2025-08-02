{{ config(materialized='view') }}

with raw as (
    select 
        id,
        date,
        message,
        sender_id,
        media,
        channel,
        raw_json
    from {{ source('raw', 'telegram_messages') }}
)

select
    id as message_id,
    date as message_timestamp,
    message,
    sender_id,
    media,
    channel,
    raw_json
from raw
where message is not null or media is not null
