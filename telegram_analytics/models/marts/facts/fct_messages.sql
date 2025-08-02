{{ config(materialized='table') }}

select
    m.message_id,
    m.message_timestamp,
    m.sender_id,
    c.channel_name,
    d.date,
    m.media,
    length(m.message) as message_length,
    case when m.media is not null then true else false end as has_media
from {{ ref('stg_telegram_messages') }} m
left join {{ ref('dim_channels') }} c
    on m.channel = c.channel_name
left join {{ ref('dim_dates') }} d
    on date_trunc('day', m.message_timestamp) = d.date
