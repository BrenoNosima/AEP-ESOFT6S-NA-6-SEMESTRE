from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import MagicMock

import mongomock
import pytest
from pymongo.errors import PyMongoError

from app.domain.exceptions import RepositoryError
from app.domain.models.consultation import Consultation
from app.domain.models.location import Location
from app.api.repositories.mongo_consultation_repository import MongoConsultationRepository


@pytest.fixture
def database():
    # tz_aware=True espelha o client real (app/database/mongodb.py).
    return mongomock.MongoClient(tz_aware=True).db


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


def test_list_all_filters_by_category(repository) -> None:
    repository.save(_make_consultation(category="agua"))
    repository.save(_make_consultation(category="residuos"))

    results = repository.list_all(category="agua")

    assert [c.category for c in results] == ["agua"]


def test_list_all_applies_limit_and_skip(repository) -> None:
    for i in range(5):
        repository.save(
            Consultation(
                question=f"Pergunta {i}",
                category="geral",
                answer="ok",
                created_at=datetime(2024, 1, i + 1, tzinfo=timezone.utc),
            )
        )

    page = repository.list_all(limit=2, skip=1)

    assert len(page) == 2


def test_pymongo_error_is_translated_into_repository_error() -> None:
    collection = MagicMock()
    collection.find.side_effect = PyMongoError("mongo indisponível")
    repository = MongoConsultationRepository({"consultations": collection})

    with pytest.raises(RepositoryError):
        repository.list_all()


def test_delete_by_user_removes_only_that_users_consultations(repository, database) -> None:
    collection = database["consultations"]
    for consultation_id, user_id in [("c1", "u1"), ("c2", "u1"), ("c3", "u2")]:
        collection.insert_one(
            {
                "_id": consultation_id,
                "user_id": user_id,
                "question": "Pergunta",
                "category": "geral",
                "answer": "Resposta",
                "created_at": datetime.now(timezone.utc),
            }
        )

    removed = repository.delete_by_user("u1")

    assert removed == 2
    assert [d["_id"] for d in collection.find()] == ["c3"]


def test_delete_by_user_returns_zero_when_user_has_no_consultations(repository) -> None:
    assert repository.delete_by_user("sem-consultas") == 0


def _make_user_consultation(user_id: str, category: str = "residuos") -> Consultation:
    return Consultation(
        question="Posso reciclar isopor?",
        category=category,
        answer="Depende.",
        user_id=user_id,
        location=Location(city="Maringá", state="PR"),
    )


def test_save_stores_user_id_and_location_subdocument(repository, database) -> None:
    consultation = _make_user_consultation("u1")

    repository.save(consultation)

    document = database["consultations"].find_one({"_id": consultation.id})
    assert document["user_id"] == "u1"
    assert document["location"] == {"city": "Maringá", "state": "PR"}


def test_get_by_id_round_trips_user_id_and_location(repository) -> None:
    consultation = _make_user_consultation("u1")
    repository.save(consultation)

    assert repository.get_by_id(consultation.id) == consultation


def test_consultation_without_user_or_location_is_saved_as_null(repository, database) -> None:
    consultation = _make_consultation()
    repository.save(consultation)

    document = database["consultations"].find_one({"_id": consultation.id})
    assert document["user_id"] is None
    assert document["location"] is None
    assert repository.get_by_id(consultation.id) == consultation


def test_legacy_document_without_user_fields_is_still_readable(repository, database) -> None:
    database["consultations"].insert_one(
        {
            "_id": "legado",
            "question": "Pergunta antiga",
            "category": "geral",
            "answer": "Resposta antiga",
            "created_at": datetime(2024, 1, 1, tzinfo=timezone.utc),
        }
    )

    found = repository.get_by_id("legado")

    assert found.user_id is None
    assert found.location is None


def test_list_all_filters_by_user_id(repository) -> None:
    mine = _make_user_consultation("u1")
    repository.save(mine)
    repository.save(_make_user_consultation("u2"))

    assert repository.list_all(user_id="u1") == [mine]


def test_list_all_combines_user_and_category_filters(repository) -> None:
    wanted = _make_user_consultation("u1", "agua")
    repository.save(wanted)
    repository.save(_make_user_consultation("u1", "residuos"))
    repository.save(_make_user_consultation("u2", "agua"))

    assert repository.list_all(user_id="u1", category="agua") == [wanted]


def test_count_by_category_groups_only_that_users_consultations(repository) -> None:
    for category in ["residuos", "residuos", "agua"]:
        repository.save(_make_user_consultation("u1", category))
    repository.save(_make_user_consultation("u2", "energia"))

    assert repository.count_by_category("u1") == {"residuos": 2, "agua": 1}


def test_count_by_category_is_empty_for_user_without_consultations(repository) -> None:
    assert repository.count_by_category("sem-consultas") == {}


def test_creates_user_id_created_at_index(repository, database) -> None:
    keys = [tuple(info["key"]) for info in database["consultations"].index_information().values()]

    assert (("user_id", 1), ("created_at", -1)) in keys
