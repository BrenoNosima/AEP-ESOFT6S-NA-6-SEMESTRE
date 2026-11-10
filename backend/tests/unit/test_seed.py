from __future__ import annotations

import mongomock
import pytest

from app.api.repositories.mongo_consultation_repository import MongoConsultationRepository
from app.api.repositories.mongo_user_repository import MongoUserRepository
from scripts.seed import seed


@pytest.fixture
def database():
    return mongomock.MongoClient(tz_aware=True).db


def test_seed_creates_users_with_addresses_and_related_consultations(database) -> None:
    created = seed(database)

    users = MongoUserRepository(database)
    consultations = MongoConsultationRepository(database)
    ana = users.get_by_id("seed-user-ana")
    assert created == {"users": 2, "consultations": 5}
    assert len(ana.addresses) == 2
    assert {c.user_id for c in consultations.list_all()} == {"seed-user-ana", "seed-user-bruno"}
    assert consultations.count_by_category("seed-user-ana") == {"residuos": 2, "agua": 1}


def test_seed_is_idempotent(database) -> None:
    seed(database)

    second_run = seed(database)

    assert second_run == {"users": 0, "consultations": 0}
    assert database["users"].count_documents({}) == 2
    assert database["consultations"].count_documents({}) == 5
