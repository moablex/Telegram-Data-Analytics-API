from sqlalchemy.orm import Session
from models import Message, Channel
from sqlalchemy import func

def get_top_products(db: Session, limit: int = 10):
    # Example: assumes messages table has column product_name
    return (
        db.query(Message.product_name, func.count().label("count"))
        .group_by(Message.product_name)
        .order_by(func.count().desc())
        .limit(limit)
        .all()
    )

def get_channel_activity(db: Session, channel_name: str):
    return (
        db.query(func.date_trunc("day", Message.message_timestamp).label("date"),
                 func.count(Message.message_id).label("message_count"))
        .join(Channel, Channel.channel_name == channel_name)
        .filter(Message.channel == channel_name)
        .group_by(func.date_trunc("day", Message.message_timestamp))
        .order_by("date")
        .all()
    )

def search_messages(db: Session, query: str):
    return (
        db.query(Message)
        .filter(Message.message.ilike(f"%{query}%"))
        .all()
    )
