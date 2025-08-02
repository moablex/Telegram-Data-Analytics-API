with dates as (
    select distinct
        date_trunc('day', message_timestamp)::date as date
    from {{ ref('stg_telegram_messages') }}
)

select
    date,
    extract(year from date) as year,
    extract(month from date) as month,
    extract(day from date) as day,
    extract(dow from date) as day_of_week,
    to_char(date, 'Day') as day_name
from dates
