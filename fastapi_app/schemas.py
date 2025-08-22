from pydantic import BaseModel
from datetime import datetime

# For top products report
class TopProduct(BaseModel):
    product_name: str
    count: int

    class Config:
        orm_mode = True

# For channel activity
class ChannelActivity(BaseModel):
    date: datetime
    message_count: int

    class Config:
        orm_mode = True

# For search messages
class MessageOut(BaseModel):
    message_id: int
    message: str
    message_timestamp: datetime
    sender_id: int
    channel: str

    class Config:
        orm_mode = True
