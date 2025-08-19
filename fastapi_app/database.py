import os
from databases import Database
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# Global database object
database = Database(DATABASE_URL)

async def connect_db():
    """Connect to the database."""
    await database.connect()

async def disconnect_db():
    """Disconnect from the database."""
    await database.disconnect()

async def get_db():
    """
    Dependency for FastAPI routes.
    Returns the connected database instance.
    """
    return database
