from unittest.mock import MagicMock

from fastapi.testclient import TestClient
from pymongo.errors import PyMongoError

from app.api.routes.health import get_database
from app.main import app

client = TestClient(app)


def _fake_database(*, ping_ok: bool) -> MagicMock:
    database = MagicMock()
    if ping_ok:
        database.client.admin.command.return_value = {"ok": 1.0}
    else:
        database.client.admin.command.side_effect = PyMongoError("indisponível")
    return database


def test_health_returns_ok_when_mongodb_responds():
    app.dependency_overrides[get_database] = lambda: _fake_database(ping_ok=True)
    try:
        response = client.get("/health")
    finally:
        app.dependency_overrides.pop(get_database, None)

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_health_returns_503_when_mongodb_unavailable():
    app.dependency_overrides[get_database] = lambda: _fake_database(ping_ok=False)
    try:
        response = client.get("/health")
    finally:
        app.dependency_overrides.pop(get_database, None)

    assert response.status_code == 503
