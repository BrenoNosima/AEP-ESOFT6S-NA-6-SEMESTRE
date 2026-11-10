from __future__ import annotations

import pytest
from pymongo import MongoClient
from pymongo.errors import PyMongoError

from app.api.repositories.mongo_consultation_repository import MongoConsultationRepository
from app.api.repositories.mongo_user_repository import MongoUserRepository
from app.api.services.user_service import UserService
from app.core.config import settings
from app.domain.exceptions import ConflictError
from app.domain.models.consultation import Consultation
from app.domain.models.location import Location
from app.domain.models.user import Address, User

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
def database():
    client = MongoClient(settings.mongodb_uri, tz_aware=True)
    database = client[TEST_DATABASE_NAME]
    yield database
    database.drop_collection("consultations")
    database.drop_collection("users")
    client.close()


@pytest.fixture
def repository(database):
    return MongoConsultationRepository(database)


@pytest.fixture
def user_repository(database):
    return MongoUserRepository(database)


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


def test_update_category_against_real_mongodb(repository) -> None:
    consultation = Consultation(
        question="Como separar lixo reciclável?",
        category="geral",
        answer="Separe papel, plástico, vidro e metal em recipientes diferentes.",
    )
    repository.save(consultation)

    updated = repository.update_category(consultation.id, "residuos")

    assert updated is not None
    assert updated.category == "residuos"


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


def _user_consultation(user_id: str, category: str) -> Consultation:
    return Consultation(
        question="Como reduzir o consumo de energia?",
        category=category,
        answer="Troque lâmpadas por LED.",
        user_id=user_id,
        location=Location(city="Maringá", state="PR"),
    )


def test_unique_email_index_rejects_duplicates_in_real_mongodb(user_repository) -> None:
    user_repository.save(User(name="Ana", email="ana@email.com"))

    with pytest.raises(ConflictError):
        user_repository.save(User(name="Outra Ana", email="ana@email.com"))


def test_add_address_pushes_subdocument_in_real_mongodb(user_repository) -> None:
    user = User(name="Ana", email="ana@email.com")
    user_repository.save(user)

    user_repository.add_address(user.id, Address(street="Rua A", city="Maringá", state="PR"))
    updated = user_repository.add_address(
        user.id, Address(street="Rua B", city="Curitiba", state="PR")
    )

    assert [a.city for a in updated.addresses] == ["Maringá", "Curitiba"]
    assert user_repository.get_by_id(user.id) == updated


def test_consultation_keeps_user_reference_and_location_in_real_mongodb(
    repository, user_repository
) -> None:
    user = User(name="Ana", email="ana@email.com")
    user_repository.save(user)
    consultation = _user_consultation(user.id, "energia")
    repository.save(consultation)

    assert repository.get_by_id(consultation.id) == consultation
    assert repository.list_all(user_id="outro-usuario") == []
    assert repository.list_all(user_id=user.id) == [consultation]


def test_count_by_category_aggregates_with_group_in_real_mongodb(repository) -> None:
    for category in ["residuos", "residuos", "agua"]:
        repository.save(_user_consultation("u1", category))
    repository.save(_user_consultation("u2", "energia"))

    assert repository.count_by_category("u1") == {"residuos": 2, "agua": 1}


def test_delete_user_cascades_to_consultations_in_real_mongodb(
    repository, user_repository
) -> None:
    service = UserService(user_repository, repository)
    ana = service.create_user("Ana", "ana@email.com")
    bia = service.create_user("Bia", "bia@email.com")
    repository.save(_user_consultation(ana.id, "agua"))
    repository.save(_user_consultation(ana.id, "energia"))
    kept = _user_consultation(bia.id, "agua")
    repository.save(kept)

    removed = service.delete_user(ana.id)

    assert removed == 2
    assert user_repository.get_by_id(ana.id) is None
    assert repository.list_all() == [kept]