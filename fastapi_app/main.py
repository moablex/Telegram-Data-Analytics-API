from fastapi import FastAPI, Depends, HTTPException
from typing import List
from database import connect_db, disconnect_db
from database import connect_db, disconnect_db, get_db

import models
from sqlalchemy.orm import Session

import crud, schemas
app = FastAPI(title="Telegram Analytics API")
import crud
@app.on_event("startup")
async def startup():
    await connect_db()

@app.on_event("shutdown")
async def shutdown():
    await disconnect_db()


from fastapi import FastAPI, Query
from typing import List
from database import connect_db, disconnect_db, database
from models import TopProduct, ChannelActivity, Message

app = FastAPI(title="Telegram Analytics API")

# Lifecycle events
@app.on_event("startup")
async def startup():
    await connect_db()

@app.on_event("shutdown")
async def shutdown():
    await disconnect_db()

# --- Endpoints ---

@app.get("/")
def read_root():
    return {"message": "Welcome to the Telegram Data Analytics API!"}
# 1. Top Products
@app.get("/api/reports/top-products", response_model=List[TopProduct])
async def get_top_products(limit: int = Query(10, ge=1)):
    query = """
        SELECT product_name, mention_count
        FROM top_products
        ORDER BY mention_count DESC
        LIMIT :limit
    """
    rows = await database.fetch_all(query=query, values={"limit": limit})
    return rows

# 2. Channel Activity
@app.get("/api/channels/{channel_name}/activity", response_model=List[ChannelActivity])
async def get_channel_activity(channel_name: str):
    query = """
        SELECT channel, day, messages_count
        FROM channel_activity
        WHERE channel = :channel_name
        ORDER BY day
    """
    rows = await database.fetch_all(query=query, values={"channel_name": channel_name})
    return rows

# 3. Search Messages
@app.get("/api/search/messages", response_model=List[Message])
async def search_messages(query: str = Query(..., min_length=1)):
    sql = """
        SELECT message_id, message_timestamp, sender_id, channel AS channel_name, message
        FROM fct_messages
        WHERE message ILIKE :search
        ORDER BY message_timestamp DESC
        LIMIT 50
    """
    rows = await database.fetch_all(sql, values={"search": f"%{query}%"})
    return rows
