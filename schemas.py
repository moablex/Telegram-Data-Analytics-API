from pydantic import BaseModel
from typing import List, Optional

class ProductCount(BaseModel):
    product_name: str
    mention_count: int

class ChannelActivity(BaseModel):
    date: str
    message_count: int

class MessageResult(BaseModel):
    id: int
    date: str
    message: str
    sender_id: Optional[int]
    channel: str
