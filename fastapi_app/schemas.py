from pydantic import BaseModel
from typing import Optional

class TopProduct(BaseModel):
    product_name: str
    mention_count: int

class ChannelActivity(BaseModel):
    channel: str
    day: str  # YYYY-MM-DD
    messages_count: int

class Message(BaseModel):
    message_id: int
    message_timestamp: str  # ISO format
    sender_id: int
    channel_name: str
    message: Optional[str] = None
