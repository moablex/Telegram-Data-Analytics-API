import os
import json
import psycopg2
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

# Get DB credentials from .env
DB_HOST = os.getenv('DB_HOST')
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASS = os.getenv('DB_PASS')
DB_PORT = os.getenv('DB_PORT')

def load_file(filepath, cursor):
    with open(filepath, 'r', encoding='utf-8') as f:
        messages = json.load(f)

    for msg in messages:
        # Skip messages with no text and no media
        if msg['media'] is None and msg['message'] is None:
            logger.info(f"Skipping message {msg['id']} – both 'media' and 'message' are null")
            continue

        logger.info(f"Inserting message {msg['id']} with media: {msg.get('media')}, media_path: {msg.get('media_path')}")

        cursor.execute("""
            INSERT INTO raw.telegram_messages
            (id, date, message, sender_id, media, media_path, channel, raw_json)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO NOTHING;
        """, (
            msg['id'],
            msg['date'],
            msg['message'],
            msg['sender_id'],
            msg['media'],
            msg.get('media_path'),
            msg['channel'],
            json.dumps(msg['raw'])
        ))

def main():
    conn = psycopg2.connect(
        host=DB_HOST, dbname=DB_NAME, user=DB_USER, password=DB_PASS, port=DB_PORT
    )
    cursor = conn.cursor()

    # Create schema and table
    cursor.execute("CREATE SCHEMA IF NOT EXISTS raw;")
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS raw.telegram_messages (
        id BIGINT PRIMARY KEY,
        date TIMESTAMP,
        message TEXT,
        sender_id BIGINT,
        media TEXT,
        media_path TEXT,
        channel TEXT,
        raw_json JSONB
    );
    """)
    conn.commit()

    # Load all JSON files
    root = './data/raw/telegram_messages'
    for day in os.listdir(root):
        folder = os.path.join(root, day)
        if os.path.isdir(folder):
            for file in os.listdir(folder):
                if file.endswith('.json'):
                    filepath = os.path.join(folder, file)
                    logger.info(f"Loading {filepath}...")
                    load_file(filepath, cursor)
                    conn.commit()

    cursor.close()
    conn.close()
    logger.info("✅ All files loaded successfully.")

if __name__ == "__main__":
    main()
