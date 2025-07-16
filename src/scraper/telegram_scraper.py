import os
import json
import asyncio
import base64
from datetime import datetime
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError, FloodWaitError, ChannelPrivateError
from telethon.tl.types import PeerUser, PeerChat, PeerChannel, Channel, Chat
from dotenv import load_dotenv
from tqdm.asyncio import tqdm_asyncio
import logging

# Load environment variables
load_dotenv()

API_ID = os.getenv("TELEGRAM_API_ID")
API_HASH = os.getenv("TELEGRAM_API_HASH")
SESSION_NAME = os.getenv("SESSION_NAME", "session")

# Configure logging
os.makedirs('logs', exist_ok=True)
logging.basicConfig(
    filename='logs/scrape.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Channels to scrape
CHANNELS = [
    "lobelia4cosmetics",
    "tikvahpharma",
    "Chemeds"
]

def serialize_dict(obj):
    """
    Recursively serialize datetime and bytes objects in a dictionary to strings.
    """
    if isinstance(obj, dict):
        return {k: serialize_dict(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [serialize_dict(item) for item in obj]
    elif isinstance(obj, datetime):
        return obj.isoformat()
    elif isinstance(obj, bytes):
        return base64.b64encode(obj).decode('utf-8')  # Convert bytes to base64 string
    return obj

async def scrape_channel(client, channel, message_limit=100):
    """
    Scrape up to message_limit messages from a channel and save to JSON.
    Args:
        client: TelegramClient instance
        channel: Channel username or ID
        message_limit: Max number of messages to scrape (default: 100)
    """
    try:
        # Verify channel accessibility
        try:
            entity = await client.get_entity(channel)
            entity_type = type(entity).__name__
            entity_id = entity.id
            entity_title = getattr(entity, 'title', 'N/A') if entity_type in ('Channel', 'Chat') else 'User'
            logger.info(f"Accessed entity: {channel} (Type: {entity_type}, ID: {entity_id}, Title: {entity_title})")

            # Check if entity is a channel or group
            if entity_type not in ('Channel', 'Chat'):
                logger.warning(f"Entity {channel} is a {entity_type}, not a channel. Skipping.")
                return
        except ChannelPrivateError:
            logger.error(f"Channel {channel} is private or inaccessible")
            return
        except Exception as e:
            logger.error(f"Cannot access channel {channel}: {str(e)}")
            return

        logger.info(f"Starting scrape for channel: {channel}")
        messages_data = []
        today = datetime.utcnow().strftime('%Y-%m-%d')
        out_dir = f"data/raw/telegram_messages/{today}"
        os.makedirs(out_dir, exist_ok=True)
        filename = f"{out_dir}/{channel}.json"

        async for message in tqdm_asyncio(client.iter_messages(channel, limit=message_limit), desc=f"Scraping {channel}"):
            try:
                m_dict = message.to_dict()

                # Handle sender_id based on from_id type
                sender_id = None
                if m_dict.get("from_id"):
                    if isinstance(m_dict["from_id"], PeerUser):
                        sender_id = m_dict["from_id"].user_id
                    elif isinstance(m_dict["from_id"], (PeerChat, PeerChannel)):
                        sender_id = m_dict["from_id"].chat_id or m_dict["from_id"].channel_id

                # Handle date serialization
                date = None
                if m_dict.get("date") and isinstance(m_dict["date"], datetime):
                    date = m_dict["date"].isoformat()

                # Extract relevant fields
                extracted = {
                    "id": m_dict.get("id"),
                    "date": date,
                    "message": m_dict.get("message"),
                    "sender_id": sender_id,
                    "media": str(type(message.media)) if message.media else None,
                    "channel": channel
                }

                # Serialize raw dict to handle datetime and bytes
                extracted["raw"] = serialize_dict(m_dict)
                messages_data.append(extracted)

            except FloodWaitError as e:
                logger.warning(f"Rate limit hit for {channel}, waiting {e.seconds} seconds")
                await asyncio.sleep(e.seconds)
                continue
            except Exception as e:
                logger.error(f"Error processing message {m_dict.get('id')} in {channel}: {str(e)}")
                continue

        # Save JSON
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(messages_data, f, ensure_ascii=False, indent=2)

        logger.info(f"Completed scrape for channel: {channel}. Total messages: {len(messages_data)}")
    except Exception as e:
        logger.error(f"Error scraping channel {channel}: {str(e)}")

async def main():
    """
    Main entry: creates client and starts scraping.
    """
    async with TelegramClient(SESSION_NAME, API_ID, API_HASH) as client:
        try:
            await client.start()
        except SessionPasswordNeededError:
            password = input("Enter your 2FA password: ")
            await client.sign_in(password=password)

        for channel in CHANNELS:
            await scrape_channel(client, channel, message_limit=100)

if __name__ == "__main__":
    asyncio.run(main())