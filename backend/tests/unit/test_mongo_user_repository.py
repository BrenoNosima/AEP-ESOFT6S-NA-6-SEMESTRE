from __future__ import annotations

from unittest.mock import MagicMock

import mongomock
import pytest
from pymongo.errors import PyMongoError

from app.api.repositories.mongo_user_repository import MongoUserRepository
from app.domain.exceptions import ConflictError, RepositoryError
from app.domain.models.user import Address, User


@pytest.fixture
def database():
    # tz_aware=True espelha o client real (app/database/mongodb.py).
    return mongomock.MongoClient(tz_aware=True).db


@pytest.fixture
def repository(database) -> MongoUserRepository:
    return MongoUserRepository(database)


def _make_user(email: str = "ana@email.com", *addresses: Address) -> User:
    return User(name="Ana", email=email, addresses=addresses)


MARINGA = Address(street="Rua A", city="Maringá", state="PR")
CURITIBA = Address(street="Rua B", city="Curitiba", state="PR")


def test_save_stores_addresses_as_list_of_subdocuments(repository, database) -> None:
    user = _make_user("ana@email.com", MARINGA)

    assert repository.save(user) == user

    document = database["users"].find_one({"_id": user.id})
    assert document["email"] == "ana@email.com"
    assert document["addresses"] == [
        {"street": "Rua A", "city": "Maringá", "state": "PR"}
    ]


def test_save_with_duplicate_email_raises_conflict(repository) -> None:
    repository.save(_make_user("ana@email.com"))

    with pytest.raises(ConflictError):
        repository.save(_make_user("ana@email.com"))


def test_get_by_id_round_trips_user_with_addresses(repository) -> None:
    user = _make_user("ana@email.com", MARINGA, CURITIBA)
    repository.save(user)

    found = repository.get_by_id(user.id)

    assert found == user
    assert found.primary_address() == MARINGA


def test_get_by_id_returns_none_when_missing(repository) -> None:
    assert repository.get_by_id("nao-existe") is None


def test_list_all_returns_newest_first_with_pagination(repository, database) -> None:
    users = [_make_user(f"u{i}@email.com") for i in range(3)]
    for index, user in enumerate(users):
        repository.save(user)
        # Força created_at distintos para a ordenação ser determinística.
        database["users"].update_one(
            {"_id": user.id}, {"$set": {"created_at": user.created_at.replace(year=2020 + index)}}
        )

    emails = [u.email for u in repository.list_all()]
    page = [u.email for u in repository.list_all(limit=1, skip=1)]

    assert emails == ["u2@email.com", "u1@email.com", "u0@email.com"]
    assert page == ["u1@email.com"]


def test_add_address_pushes_into_existing_list(repository) -> None:
    user = _make_user("ana@email.com", MARINGA)
    repository.save(user)

    updated = repository.add_address(user.id, CURITIBA)

    assert updated.addresses == (MARINGA, CURITIBA)
    assert repository.get_by_id(user.id).addresses == (MARINGA, CURITIBA)


def test_add_address_returns_none_when_user_missing(repository) -> None:
    assert repository.add_address("nao-existe", MARINGA) is None


def test_delete_removes_user(repository) -> None:
    user = _make_user()
    repository.save(user)

    assert repository.delete(user.id) is True
    assert repository.get_by_id(user.id) is None
    assert repository.delete(user.id) is False


def test_document_without_addresses_field_is_read_as_empty(repository, database) -> None:
    user = _make_user()
    repository.save(user)
    database["users"].update_one({"_id": user.id}, {"$unset": {"addresses": ""}})

    assert repository.get_by_id(user.id).addresses == ()


def test_pymongo_error_is_translated_into_repository_error() -> None:
    database = MagicMock()
    database.__getitem__.return_value.find.side_effect = PyMongoError("down")
    repository = MongoUserRepository(database)

    with pytest.raises(RepositoryError):
        repository.list_all()
