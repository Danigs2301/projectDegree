from pymongo import MongoClient
from pymongo.database import Database
from data.infrastructure.config import settings

_client: MongoClient = None

def get_client() -> MongoClient:
    global _client
    if _client is None:
        _client = MongoClient(settings.MONGO_URI)
    return _client

def get_db() -> Database:
    return get_client()[settings.MONGO_DB]

def close_connection():
    global _client
    if _client is not None:
        _client.close()
        _client = None