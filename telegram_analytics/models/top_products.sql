-- models/top_products.sql

with extracted_products as (
    select
        -- Extract product names using regex matching (case insensitive)
        lower(trim(product)) as product_name
    from (
        select
            -- regexp_matches returns an array, we unnest it
            unnest(regexp_matches(message, '(?i)(paracetamol|aspirin|ibuprofen|vitamin c|amoxicillin|metformin|atorvastatin)', 'g')) as product
        from {{ ref('fct_messages') }}
        where message is not null
    ) sub
),

product_counts as (
    select
        product_name,
        count(*) as mention_count
    from extracted_products
    where product_name is not null
    group by product_name
)

select
    product_name,
    mention_count
from product_counts
order by mention_count desc
