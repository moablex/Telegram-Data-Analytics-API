with messages_with_date as (
    select
        channel as channel, 
        date::date as day,
        count(*) as messages_count
    from {{ ref('fct_messages') }}
    where date is not null
    group by 1, 2
)

select
    channel,
    day,
    messages_count
from messages_with_date
order by channel, day
