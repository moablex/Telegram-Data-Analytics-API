# Telegram-Data-Analytics-API/fastapi_app/main.py
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from database import connect_db, disconnect_db
import crud
import models

app = FastAPI(title="Telegram Analytics API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.on_event("startup")
async def startup():
    await connect_db()

@app.on_event("shutdown")
async def shutdown():
    await disconnect_db()

@app.get("/api/reports/top-products", response_model=List[models.TopProduct])
async def top_products(limit: int = Query(10, ge=1, le=100)):
    return await crud.get_top_products(limit)

@app.get("/api/channels/{channel_name}/activity", response_model=List[models.ChannelActivity])
async def channel_activity(channel_name: str):
    results = await crud.get_channel_activity(channel_name)
    if not results:
        raise HTTPException(status_code=404, detail="Channel not found or no activity")
    return results

@app.get("/api/search/messages", response_model=List[models.Message])
async def search_messages(query: str = Query(..., min_length=2)):
    return await crud.search_messages(query)
