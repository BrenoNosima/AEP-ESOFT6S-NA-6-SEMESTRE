from __future__ import annotations

from datetime import datetime, timezone

import mongomock
import pytest

from app.domain.models.consultation import Consultation
from app.repositories.mongo_consultation_repository import MongoConsultationRepository


@pytest.fixture
def database():
    return mongomock.MongoClient().db


@pytest.fixture
def repository(database) -> MongoConsultationRepository:
    return MongoConsultationRepository(database)


def _make_consultation(
    question: str = "Posso reciclar isopor?",
    category: str = "residuos",
    answer: str = "Depende do serviço de coleta seletiva da sua cidade.",
) -> Consultation:
    return Consultation(question=question, category=category, answer=answer)


def test_save_persists_using_consultation_id_as_mongo_id(repository, database) -> None:
    consultation = _make_consultation()

    saved = repository.save(consultation)

    assert saved == consultation
    document = database["consultations"].find_one({"_id": consultation.id})
    assert document is not None
    assert document["question"] == consultation.question


def test_get_by_id_returns_the_saved_consultation(repository) -> None:
    consultation = _make_consultation()
    repository.save(consultation)

    found = repository.get_by_id(consultation.id)

    assert found == consultation


def test_get_by_id_returns_none_when_not_found(repository) -> None:
    assert repository.get_by_id("id-inexistente") is None


def test_list_all_returns_consultations_ordered_by_created_at_desc(repository) -> None:
    older = Consultation(
        question="Pergunta antiga",
        category="agua",
        answer="Resposta antiga",
        created_at=datetime(2024, 1, 1, tzinfo=timezone.utc),
    )
    newer = Consultation(
        question="Pergunta nova",
        category="agua",
        answer="Resposta nova",
        created_at=datetime(2024, 6, 1, tzinfo=timezone.utc),
    )
    repository.save(older)
    repository.save(newer)

    results = repository.list_all()

    assert [consultation.id for consultation in results] == [newer.id, older.id]


def test_delete_removes_existing_consultation(repository) -> None:
    consultation = _make_consultation()
    repository.save(consultation)

    deleted = repository.delete(consultation.id)

    assert deleted is True
    assert repository.get_by_id(consultation.id) is None


def test_delete_returns_false_when_not_found(repository) -> None:
    assert repository.delete("id-inexistente") is False


def test_update_category_changes_only_the_category(repository) -> None:
    consultation = _make_consultation(category="agua")
    repository.save(consultation)

    updated = repository.update_category(consultation.id, "residuos")

    assert updated is not None
    assert updated.category == "residuos"
    assert updated.question == consultation.question
    assert updated.answer == consultation.answer
    assert repository.get_by_id(consultation.id).category == "residuos"


def test_update_category_returns_none_when_not_found(repository) -> None:
    assert repository.update_category("id-inexistente", "residuos") is None
