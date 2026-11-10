from __future__ import annotations

import mongomock
import pytest
from fastapi.testclient import TestClient

from app.api.dependencies import get_llm_provider
from app.database.mongodb import get_database
from app.llm.providers.fake_provider import FakeLLMProvider
from app.main import app


@pytest.fixture
def test_database():
    return mongomock.MongoClient(tz_aware=True).db


@pytest.fixture
def client(test_database) -> TestClient:
    app.dependency_overrides[get_llm_provider] = lambda: FakeLLMProvider(
        "Descarte em ponto de coleta."
    )
    app.dependency_overrides[get_database] = lambda: test_database

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
