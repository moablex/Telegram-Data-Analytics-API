import os
import json
import asyncio
import base64
from datetime import datetime
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError, FloodWaitError, ChannelPrivateError
from telethon.tl.types import PeerUser, PeerChat, PeerChannel, Channel, Chat, MessageMediaPhoto
from dotenv import load_dotenv
from tqdm.asyncio import tqdm_asyncio
import logging

# Load environment variables
load_dotenv()

API_ID = os.getenv("TELEGRAM_API_ID")
API_HASH = os.getenv("TELEGRAM_API_HASH")
SESSION_NAME = os.getenv("SESSION_NAME", "session")

# Logging
os.makedirs('logs', exist_ok=True)
logging.basicConfig(
    filename='logs/scrape.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# List of channels to scrape
CHANNELS = [
    "lobelia4cosmetics",
    "tikvahpharma",
    "Chemeds"
]

def serialize_dict(obj):
    if isinstance(obj, dict):
        return {k: serialize_dict(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [serialize_dict(item) for item in obj]
    elif isinstance(obj, datetime):
        return obj.isoformat()
    elif isinstance(obj, bytes):
        return base64.b64encode(obj).decode('utf-8')
    return obj

async def scrape_channel(client, channel, message_limit=100):
    try:
        try:
            entity = await client.get_entity(channel)
            entity_type = type(entity).__name__
            if entity_type not in ('Channel', 'Chat'):
                logger.warning(f"{channel} is a {entity_type}. Skipping.")
                return
        except ChannelPrivateError:
            logger.error(f"Channel {channel} is private.")
            return
        except Exception as e:
            logger.error(f"Error accessing {channel}: {e}")
            return

        messages_data = []
        today = datetime.utcnow().strftime('%Y-%m-%d')
        out_dir = f"data/raw/telegram_messages/{today}"
        os.makedirs(out_dir, exist_ok=True)
        filename = f"{out_dir}/{channel}.json"

        async for message in tqdm_asyncio(client.iter_messages(channel, limit=message_limit), desc=f"Scraping {channel}"):
            try:
                m_dict = message.to_dict()

                sender_id = None
                if m_dict.get("from_id"):
                    if isinstance(m_dict["from_id"], PeerUser):
                        sender_id = m_dict["from_id"].user_id
                    elif isinstance(m_dict["from_id"], (PeerChat, PeerChannel)):
                        sender_id = m_dict["from_id"].chat_id or m_dict["from_id"].channel_id

                date = m_dict.get("date").isoformat() if isinstance(m_dict.get("date"), datetime) else None
                media_type = str(type(message.media)) if message.media else None
                media_path = None

                # Download image if media is photo
                if isinstance(message.media, MessageMediaPhoto):
                    try:
                        media_dir = f"data/images/{channel}"
                        os.makedirs(media_dir, exist_ok=True)
                        file_path = f"{media_dir}/msg_{m_dict['id']}.jpg"
                        downloaded_file = await client.download_media(message.media, file=file_path)
                        if downloaded_file:
                            media_path = os.path.relpath(downloaded_file)
                    except Exception as e:
                        logger.warning(f"Media download failed for {channel} msg {m_dict['id']}: {e}")

                extracted = {
                    "id": m_dict.get("id"),
                    "date": date,
                    "message": m_dict.get("message"),
                    "sender_id": sender_id,
                    "media": media_type,
                    "media_path": media_path,
                    "channel": channel,
                    "raw": serialize_dict(m_dict)
                }
                messages_data.append(extracted)
            except FloodWaitError as e:
                logger.warning(f"Flood wait hit for {channel}: {e.seconds}s")
                await asyncio.sleep(e.seconds)
                continue
            except Exception as e:
                logger.error(f"Message error in {channel}: {e}")
                continue

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(messages_data, f, ensure_ascii=False, indent=2)

        logger.info(f"Completed scraping {channel}. Total messages: {len(messages_data)}")

    except Exception as e:
        logger.error(f"Channel scrape failed: {channel}: {e}")

async def main():
    async with TelegramClient(SESSION_NAME, API_ID, API_HASH) as client:
        try:
            await client.start()
        except SessionPasswordNeededError:
            pw = input("Enter 2FA password: ")
            await client.sign_in(password=pw)

        for channel in CHANNELS:
            await scrape_channel(client, channel, message_limit=100)

if __name__ == "__main__":
    asyncio.run(main())
