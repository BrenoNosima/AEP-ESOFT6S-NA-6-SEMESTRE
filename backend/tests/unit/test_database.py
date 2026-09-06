from pymongo.database import Database

from app.core.config import settings
from app.database.mongodb import get_database


def test_get_database_returns_configured_database():
    get_database.cache_clear()
    database = get_database()

    assert isinstance(database, Database)
    assert database.name == settings.mongodb_db_name
