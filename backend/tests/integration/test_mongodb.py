from __future__ import annotations

import pytest
from pymongo import MongoClient
from pymongo.errors import PyMongoError

from app.core.config import settings
from app.domain.models.consultation import Consultation
from app.repositories.mongo_consultation_repository import MongoConsultationRepository

TEST_DATABASE_NAME = "ecomentor_test"


def _mongo_is_available() -> bool:
    try:
        client = MongoClient(settings.mongodb_uri, serverSelectionTimeoutMS=500)
        client.admin.command("ping")
        return True
    except PyMongoError:
        return False


pytestmark = pytest.mark.skipif(
    not _mongo_is_available(),
    reason="MongoDB não está acessível em settings.mongodb_uri; pulando testes de integração.",
)


@pytest.fixture
def repository():
    client = MongoClient(settings.mongodb_uri, tz_aware=True)
    database = client[TEST_DATABASE_NAME]
    yield MongoConsultationRepository(database)
    database.drop_collection("consultations")
    client.close()


def test_save_and_get_by_id_round_trip_against_real_mongodb(repository) -> None:
    consultation = Consultation(
        question="Como descarto pilhas usadas?",
        category="residuos",
        answer="Leve a um ponto de coleta adequado.",
    )

    repository.save(consultation)
    found = repository.get_by_id(consultation.id)

    assert found == consultation


def test_list_all_returns_saved_consultations(repository) -> None:
    consultation = Consultation(
        question="Como economizar água em casa?",
        category="agua",
        answer="Reduza o tempo de banho e conserte vazamentos.",
    )
    repository.save(consultation)

    results = repository.list_all()

    assert consultation in results


def test_delete_removes_from_real_mongodb(repository) -> None:
    consultation = Consultation(
        question="Posso jogar óleo de cozinha na pia?",
        category="residuos",
        answer="Não. Armazene em garrafa e leve a um ponto de coleta.",
    )
    repository.save(consultation)

    deleted = repository.delete(consultation.id)

    assert deleted is True
    assert repository.get_by_id(consultation.id) is None
