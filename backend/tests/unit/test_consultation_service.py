from __future__ import annotations

from dataclasses import replace

import pytest

from app.domain.exceptions import NotFoundError
from app.domain.interfaces.consultation_repository import ConsultationRepository
from app.domain.interfaces.llm_provider import LLMProvider
from app.domain.interfaces.user_repository import UserRepository
from app.domain.models.consultation import Consultation
from app.domain.models.location import Location
from app.domain.models.user import Address, User
from app.api.services.consultation_service import ConsultationService
from app.api.services.sustainability_service import SustainabilityService


class FakeLLMProvider(LLMProvider):
    def __init__(self, fixed_response: str) -> None:
        self.fixed_response = fixed_response
        self.received_prompt: str | None = None

    def generate_response(self, prompt: str) -> str:
        self.received_prompt = prompt
        return self.fixed_response


class ScriptedLLMProvider(LLMProvider):
    """Devolve as respostas na ordem dada (1ª: classificação, 2ª: orientação)."""

    def __init__(self, *responses: str) -> None:
        self._responses = list(responses)
        self.prompts: list[str] = []

    def generate_response(self, prompt: str) -> str:
        self.prompts.append(prompt)
        return self._responses.pop(0)


class FakeUserRepository(UserRepository):
    def __init__(self, *users: User) -> None:
        self._storage = {user.id: user for user in users}

    def get_by_id(self, user_id: str) -> User | None:
        return self._storage.get(user_id)

    # Métodos do contrato que o ConsultationService não usa.
    def save(self, user: User) -> User:
        raise NotImplementedError

    def list_all(self, *, limit: int = 50, skip: int = 0) -> list[User]:
        raise NotImplementedError

    def add_address(self, user_id: str, address: Address) -> User | None:
        raise NotImplementedError

    def delete(self, user_id: str) -> bool:
        raise NotImplementedError


_HOME = Address(street="Rua das Flores, 100", city="Maringá", state="PR")
_USER = User(name="Ana", email="ana@example.com", addresses=(_HOME,))
_HOMELESS = User(name="Bia", email="bia@example.com")


class FakeConsultationRepository(ConsultationRepository):
    def __init__(self) -> None:
        self._storage: dict[str, Consultation] = {}

    def save(self, consultation: Consultation) -> Consultation:
        self._storage[consultation.id] = consultation
        return consultation

    def list_all(
        self,
        *,
        category: str | None = None,
        user_id: str | None = None,
        limit: int = 50,
        skip: int = 0,
    ) -> list[Consultation]:
        items = list(self._storage.values())
        if category is not None:
            items = [c for c in items if c.category == category]
        if user_id is not None:
            items = [c for c in items if c.user_id == user_id]
        return items[skip : skip + limit]

    def count_by_category(self, user_id: str) -> dict[str, int]:
        counts: dict[str, int] = {}
        for c in self._storage.values():
            if c.user_id == user_id:
                counts[c.category] = counts.get(c.category, 0) + 1
        return counts

    def get_by_id(self, consultation_id: str) -> Consultation | None:
        return self._storage.get(consultation_id)

    def delete(self, consultation_id: str) -> bool:
        return self._storage.pop(consultation_id, None) is not None

    def delete_by_user(self, user_id: str) -> int:
        return 0

    def update_category(self, consultation_id: str, category: str) -> Consultation | None:
        existing = self._storage.get(consultation_id)
        if existing is None:
            return None
        updated = replace(existing, category=category)
        self._storage[consultation_id] = updated
        return updated


def _make_service(
    fixed_answer: str = "Leve o óleo usado a um ponto de coleta.",
    provider: LLMProvider | None = None,
):
    provider = provider or FakeLLMProvider(fixed_answer)
    sustainability_service = SustainabilityService(provider)
    repository = FakeConsultationRepository()
    users = FakeUserRepository(_USER, _HOMELESS)
    service = ConsultationService(sustainability_service, repository, users)
    return service, repository, provider


def test_create_consultation_calls_sustainability_service_with_the_question() -> None:
    service, _, provider = _make_service()

    service.create_consultation(_USER.id, "Posso reciclar isopor?", "residuos")

    assert provider.received_prompt is not None
    assert "Posso reciclar isopor?" in provider.received_prompt


def test_create_consultation_persists_answer_generated_by_sustainability_service() -> None:
    service, repository, _ = _make_service(fixed_answer="Resposta sustentável gerada.")

    created = service.create_consultation(_USER.id, "O que fazer com pilhas usadas?", "residuos")

    assert created.answer == "Resposta sustentável gerada."
    assert repository.get_by_id(created.id) == created


def test_create_consultation_keeps_question_and_category() -> None:
    service, _, _ = _make_service()

    created = service.create_consultation(_USER.id, "Posso reciclar isopor?", "residuos")

    assert created.question == "Posso reciclar isopor?"
    assert created.category == "residuos"


def test_list_consultations_returns_all_from_repository() -> None:
    service, _, _ = _make_service()
    first = service.create_consultation(_USER.id, "Pergunta 1", "residuos")
    second = service.create_consultation(_USER.id, "Pergunta 2", "agua")

    results = service.list_consultations()

    assert {c.id for c in results} == {first.id, second.id}


def test_list_consultations_returns_empty_list_when_no_consultations() -> None:
    service, _, _ = _make_service()

    assert service.list_consultations() == []


def test_get_consultation_returns_existing_consultation() -> None:
    service, _, _ = _make_service()
    created = service.create_consultation(_USER.id, "Pergunta", "residuos")

    assert service.get_consultation(created.id) == created


def test_get_consultation_raises_not_found_when_missing() -> None:
    service, _, _ = _make_service()

    with pytest.raises(NotFoundError, match="Consulta não encontrada."):
        service.get_consultation("id-inexistente")


def test_delete_consultation_removes_it() -> None:
    service, repository, _ = _make_service()
    created = service.create_consultation(_USER.id, "Pergunta", "residuos")

    service.delete_consultation(created.id)

    assert repository.get_by_id(created.id) is None


def test_delete_consultation_raises_not_found_when_missing() -> None:
    service, _, _ = _make_service()

    with pytest.raises(NotFoundError):
        service.delete_consultation("id-inexistente")


def test_update_consultation_category_changes_only_the_category() -> None:
    service, _, _ = _make_service()
    created = service.create_consultation(_USER.id, "Pergunta", "geral")

    updated = service.update_consultation_category(created.id, "residuos")

    assert updated.category == "residuos"
    assert updated.question == created.question
    assert updated.answer == created.answer


def test_update_consultation_category_raises_not_found_when_missing() -> None:
    service, _, _ = _make_service()

    with pytest.raises(NotFoundError):
        service.update_consultation_category("id-inexistente", "agua")


def test_list_consultations_filters_by_category() -> None:
    service, _, _ = _make_service()
    service.create_consultation(_USER.id, "P1", "agua")
    service.create_consultation(_USER.id, "P2", "residuos")

    results = service.list_consultations(category="agua")

    assert [c.category for c in results] == ["agua"]


def test_create_consultation_raises_not_found_and_skips_llm_when_user_missing() -> None:
    service, repository, provider = _make_service()

    with pytest.raises(NotFoundError, match="Usuário não encontrado."):
        service.create_consultation("id-inexistente", "Pergunta", "agua")

    assert provider.received_prompt is None
    assert repository.list_all() == []


def test_create_consultation_links_user_and_snapshots_primary_address() -> None:
    service, _, provider = _make_service()

    created = service.create_consultation(_USER.id, "Onde descarto pilhas?", "residuos")

    assert created.user_id == _USER.id
    assert created.location == Location(city="Maringá", state="PR")
    assert "Maringá" in provider.received_prompt
    assert "PR" in provider.received_prompt


def test_create_consultation_without_address_has_no_location() -> None:
    service, _, provider = _make_service()

    created = service.create_consultation(_HOMELESS.id, "Onde descarto pilhas?", "residuos")

    assert created.location is None
    assert "não foi informada" in provider.received_prompt


def test_create_consultation_classifies_category_when_missing() -> None:
    provider = ScriptedLLMProvider("agua", "Feche a torneira ao escovar os dentes.")
    service, _, _ = _make_service(provider=provider)

    created = service.create_consultation(_USER.id, "Como economizar água?")

    assert created.category == "agua"
    assert created.answer == "Feche a torneira ao escovar os dentes."
    assert len(provider.prompts) == 2
    assert "Classifique" in provider.prompts[0]


def test_create_consultation_does_not_classify_when_category_given() -> None:
    provider = ScriptedLLMProvider("Feche a torneira ao escovar os dentes.")
    service, _, _ = _make_service(provider=provider)

    created = service.create_consultation(_USER.id, "Como economizar água?", "agua")

    assert created.category == "agua"
    assert len(provider.prompts) == 1
