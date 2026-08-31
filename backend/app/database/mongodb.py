from __future__ import annotations

from functools import lru_cache

from pymongo import MongoClient
from pymongo.database import Database

from app.core.config import settings


@lru_cache
def get_database() -> Database:
    """Retorna a instância (singleton) do banco MongoDB usado pela aplicação."""
    client: MongoClient = MongoClient(settings.mongodb_uri, tz_aware=True)
    return client[settings.mongodb_db_name]
