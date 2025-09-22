import os
from typing import Optional

from pymongo import MongoClient
from pymongo.collection import Collection
from dotenv import load_dotenv

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
MONGODB_DB = os.getenv("MONGODB_DB", "monitordos")
MONGODB_COLLECTION = os.getenv("MONGODB_COLLECTION", "events")

_client: Optional[MongoClient] = None


def get_client() -> MongoClient:
    global _client
    if _client is None:
        _client = MongoClient(MONGODB_URI)
    return _client


def get_collection(name: Optional[str] = None) -> Collection:
    client = get_client()
    db = client[MONGODB_DB]
    coll_name = name or MONGODB_COLLECTION
    return db[coll_name]
