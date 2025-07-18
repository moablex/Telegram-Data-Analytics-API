import os
import json
import psycopg2
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv('DB_HOST')
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASS = os.getenv('DB_PASS')
DB_PORT = os.getenv('DB_PORT')

def load_file(filepath, cursor):
    with open(filepath, 'r', encoding='utf-8') as f:
        messages = json.load(f)

    for msg in messages:
        cursor.execute("""
            INSERT INTO raw.telegram_messages
            (id, date, message, sender_id, media, channel, raw_json)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO NOTHING;
        """, (
            msg['id'],
            msg['date'],
            msg['message'],
            msg['sender_id'],
            msg['media'],
            msg['channel'],
            json.dumps(msg['raw'])
        ))

def main():
    conn = psycopg2.connect(
        host=DB_HOST, dbname=DB_NAME, user=DB_USER, password=DB_PASS, port=DB_PORT
    )
    cursor = conn.cursor()

    # Create schema & table if not exists
    cursor.execute("CREATE SCHEMA IF NOT EXISTS raw;")
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS raw.telegram_messages (
        id BIGINT PRIMARY KEY,
        date TIMESTAMP,
        message TEXT,
        sender_id BIGINT,
        media TEXT,
        channel TEXT,
        raw_json JSONB
    );
    """)
    conn.commit()

    # Load all json files
    root = '/home/ablex/Development/AI/kifiya_weak7/Telegram-Data-Analytics-API/data/raw/telegram_messages'
    for day in os.listdir(root):
        folder = os.path.join(root, day)
        if os.path.isdir(folder):
            for file in os.listdir(folder):
                if file.endswith('.json'):
                    filepath = os.path.join(folder, file)
                    print(f"Loading {filepath}...")
                    load_file(filepath, cursor)
                    conn.commit()

    conn.commit()
    cursor.close()
    conn.close()
    print("Done.")

if __name__ == "__main__":
    main()
