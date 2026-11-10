from __future__ import annotations

from dataclasses import replace

import pytest

from app.api.services.user_service import UserService
from app.domain.exceptions import ConflictError, NotFoundError
from app.domain.interfaces.consultation_repository import ConsultationRepository
from app.domain.interfaces.user_repository import UserRepository
from app.domain.models.consultation import Consultation
from app.domain.models.user import Address, User


class FakeUserRepository(UserRepository):
    def __init__(self) -> None:
        self._storage: dict[str, User] = {}
        self._emails: set[str] = set()

    def save(self, user: User) -> User:
        if user.email in self._emails:
            raise ConflictError("E-mail já cadastrado.")
        self._emails.add(user.email)
        self._storage[user.id] = user
        return user

    def get_by_id(self, user_id: str) -> User | None:
        return self._storage.get(user_id)

    def list_all(self, *, limit: int = 50, skip: int = 0) -> list[User]:
        return list(self._storage.values())[skip : skip + limit]

    def add_address(self, user_id: str, address: Address) -> User | None:
        existing = self._storage.get(user_id)
        if existing is None:
            return None
        updated = existing.with_address(address)
        self._storage[user_id] = updated
        return updated

    def delete(self, user_id: str) -> bool:
        user = self._storage.pop(user_id, None)
        if user is None:
            return False
        self._emails.discard(user.email)
        return True


class FakeConsultationRepository(ConsultationRepository):
    def __init__(self) -> None:
        self._storage: dict[str, Consultation] = {}
        self.delete_by_user_calls: list[str] = []

    def add_for_user(self, user_id: str, category: str = "geral") -> str:
        consultation = Consultation(
            question="Pergunta", category=category, answer="Resposta", user_id=user_id
        )
        self._storage[consultation.id] = consultation
        return consultation.id

    def ids_of(self, user_id: str) -> list[str]:
        return [c.id for c in self._storage.values() if c.user_id == user_id]

    def delete_by_user(self, user_id: str) -> int:
        self.delete_by_user_calls.append(user_id)
        removed = self.ids_of(user_id)
        for consultation_id in removed:
            del self._storage[consultation_id]
        return len(removed)

    def list_all(
        self,
        *,
        category: str | None = None,
        user_id: str | None = None,
        limit: int = 50,
        skip: int = 0,
    ) -> list[Consultation]:
        items = [c for c in self._storage.values() if user_id is None or c.user_id == user_id]
        return items[skip : skip + limit]

    def count_by_category(self, user_id: str) -> dict[str, int]:
        counts: dict[str, int] = {}
        for consultation in self._storage.values():
            if consultation.user_id == user_id:
                counts[consultation.category] = counts.get(consultation.category, 0) + 1
        return counts

    # Métodos do contrato que o UserService não usa.
    def save(self, consultation: Consultation) -> Consultation:
        raise NotImplementedError

    def get_by_id(self, consultation_id: str) -> Consultation | None:
        raise NotImplementedError

    def delete(self, consultation_id: str) -> bool:
        raise NotImplementedError

    def update_category(self, consultation_id: str, category: str) -> Consultation | None:
        raise NotImplementedError


_HOME = Address(street="Rua das Flores, 100", city="Maringá", state="PR")
_WORK = Address(street="Av. Brasil, 500", city="Curitiba", state="PR")


@pytest.fixture
def users() -> FakeUserRepository:
    return FakeUserRepository()


@pytest.fixture
def consultations() -> FakeConsultationRepository:
    return FakeConsultationRepository()


@pytest.fixture
def service(users, consultations) -> UserService:
    return UserService(users, consultations)


def test_create_user_persists_with_addresses(service, users) -> None:
    created = service.create_user("Ana", "ana@example.com", [_HOME])

    assert created.name == "Ana"
    assert created.email == "ana@example.com"
    assert created.addresses == (_HOME,)
    assert users.get_by_id(created.id) == created


def test_create_user_without_addresses(service) -> None:
    created = service.create_user("Ana", "ana@example.com")

    assert created.addresses == ()


def test_create_user_propagates_conflict_on_duplicate_email(service) -> None:
    service.create_user("Ana", "ana@example.com")

    with pytest.raises(ConflictError):
        service.create_user("Outra Ana", "ana@example.com")


def test_get_user_returns_existing(service) -> None:
    created = service.create_user("Ana", "ana@example.com")

    assert service.get_user(created.id) == created


def test_get_user_raises_not_found_when_missing(service) -> None:
    with pytest.raises(NotFoundError, match="Usuário não encontrado."):
        service.get_user("id-inexistente")


def test_list_users_applies_limit_and_skip(service) -> None:
    created = [service.create_user(f"U{i}", f"u{i}@example.com") for i in range(3)]

    assert service.list_users() == created
    assert service.list_users(limit=1, skip=1) == [created[1]]


def test_add_address_appends_to_existing_addresses(service) -> None:
    created = service.create_user("Ana", "ana@example.com", [_HOME])

    updated = service.add_address(created.id, _WORK)

    assert updated.addresses == (_HOME, _WORK)
    assert service.get_user(created.id).addresses == (_HOME, _WORK)


def test_add_address_raises_not_found_when_user_missing(service) -> None:
    with pytest.raises(NotFoundError):
        service.add_address("id-inexistente", _HOME)


def test_delete_user_removes_user_and_only_their_consultations(
    service, consultations
) -> None:
    ana = service.create_user("Ana", "ana@example.com")
    bia = service.create_user("Bia", "bia@example.com")
    consultations.add_for_user(ana.id)
    consultations.add_for_user(ana.id)
    bia_consultation = consultations.add_for_user(bia.id)

    removed = service.delete_user(ana.id)

    assert removed == 2
    assert consultations.ids_of(ana.id) == []
    assert consultations.ids_of(bia.id) == [bia_consultation]
    with pytest.raises(NotFoundError):
        service.get_user(ana.id)
    assert service.get_user(bia.id) == bia


def test_delete_user_returns_zero_when_user_has_no_consultations(service) -> None:
    ana = service.create_user("Ana", "ana@example.com")

    assert service.delete_user(ana.id) == 0


def test_delete_user_raises_not_found_and_skips_cascade_when_missing(
    service, consultations
) -> None:
    with pytest.raises(NotFoundError):
        service.delete_user("id-inexistente")

    assert consultations.delete_by_user_calls == []


def test_delete_user_frees_email_for_reuse(service) -> None:
    ana = service.create_user("Ana", "ana@example.com")
    service.delete_user(ana.id)

    again = service.create_user("Ana", "ana@example.com")

    assert again.id != ana.id


def test_list_consultations_returns_only_that_users_history(service, consultations) -> None:
    ana = service.create_user("Ana", "ana@example.com")
    bia = service.create_user("Bia", "bia@example.com")
    first = consultations.add_for_user(ana.id)
    second = consultations.add_for_user(ana.id)
    consultations.add_for_user(bia.id)

    history = service.list_consultations(ana.id)

    assert {c.id for c in history} == {first, second}
    assert [c.id for c in service.list_consultations(ana.id, limit=1, skip=1)] == [second]


def test_list_consultations_raises_not_found_when_user_missing(service) -> None:
    with pytest.raises(NotFoundError):
        service.list_consultations("id-inexistente")


def test_summarize_consultations_counts_by_category(service, consultations) -> None:
    ana = service.create_user("Ana", "ana@example.com")
    consultations.add_for_user(ana.id, "agua")
    consultations.add_for_user(ana.id, "agua")
    consultations.add_for_user(ana.id, "residuos")

    assert service.summarize_consultations(ana.id) == {"agua": 2, "residuos": 1}


def test_summarize_consultations_raises_not_found_when_user_missing(service) -> None:
    with pytest.raises(NotFoundError):
        service.summarize_consultations("id-inexistente")
