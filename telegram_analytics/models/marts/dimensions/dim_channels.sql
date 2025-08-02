{{ config(materialized='view') }}

select distinct
    channel as channel_name
from {{ ref('stg_telegram_messages') }}
where channel is not null
