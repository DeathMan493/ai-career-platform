from functools import lru_cache

from pymongo import MongoClient
from pymongo.database import Database

from app.core.config import settings


@lru_cache
def get_mongo_client() -> MongoClient:
    return MongoClient(settings.mongodb_uri)


def get_database() -> Database:
    client = get_mongo_client()
    return client[settings.mongodb_database]
