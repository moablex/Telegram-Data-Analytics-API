from database import database

async def get_top_products(limit: int = 10):
    query = """
    SELECT product_name, mention_count
    FROM analytics.top_products
    ORDER BY mention_count DESC
    LIMIT :limit
    """
    return await database.fetch_all(query=query, values={"limit": limit})

async def get_channel_activity(channel_name: str):
    query = """
    SELECT channel, day, messages_count
    FROM analytics.channel_activity
    WHERE channel = :channel_name
    ORDER BY day
    """
    return await database.fetch_all(query=query, values={"channel_name": channel_name})

async def search_messages(query_str: str):
    query = """
    SELECT message_id, message_timestamp, sender_id, channel_name, message
    FROM analytics.fct_messages
    WHERE message ILIKE '%' || :query_str || '%'
    ORDER BY message_timestamp DESC
    LIMIT 50
    """
    return await database.fetch_all(query=query, values={"query_str": query_str})
