from __future__ import annotations

from dataclasses import replace

from app.domain.interfaces.consultation_repository import ConsultationRepository
from app.domain.interfaces.llm_provider import LLMProvider
from app.domain.models.consultation import Consultation
from app.services.consultation_service import ConsultationService
from app.services.sustainability_service import SustainabilityService


class FakeLLMProvider(LLMProvider):
    def __init__(self, fixed_response: str) -> None:
        self.fixed_response = fixed_response
        self.received_prompt: str | None = None

    def generate_response(self, prompt: str) -> str:
        self.received_prompt = prompt
        return self.fixed_response


class FakeConsultationRepository(ConsultationRepository):
    def __init__(self) -> None:
        self._storage: dict[str, Consultation] = {}

    def save(self, consultation: Consultation) -> Consultation:
        self._storage[consultation.id] = consultation
        return consultation

    def list_all(self) -> list[Consultation]:
        return list(self._storage.values())

    def get_by_id(self, consultation_id: str) -> Consultation | None:
        return self._storage.get(consultation_id)

    def delete(self, consultation_id: str) -> bool:
        return self._storage.pop(consultation_id, None) is not None

    def update_category(self, consultation_id: str, category: str) -> Consultation | None:
        existing = self._storage.get(consultation_id)
        if existing is None:
            return None
        updated = replace(existing, category=category)
        self._storage[consultation_id] = updated
        return updated


def _make_service(fixed_answer: str = "Leve o óleo usado a um ponto de coleta."):
    provider = FakeLLMProvider(fixed_answer)
    sustainability_service = SustainabilityService(provider)
    repository = FakeConsultationRepository()
    return ConsultationService(sustainability_service, repository), repository, provider


def test_create_consultation_calls_sustainability_service_with_the_question() -> None:
    service, _, provider = _make_service()

    service.create_consultation("Posso reciclar isopor?", "residuos")

    assert provider.received_prompt is not None
    assert "Posso reciclar isopor?" in provider.received_prompt


def test_create_consultation_persists_answer_generated_by_sustainability_service() -> None:
    service, repository, _ = _make_service(fixed_answer="Resposta sustentável gerada.")

    created = service.create_consultation("O que fazer com pilhas usadas?", "residuos")

    assert created.answer == "Resposta sustentável gerada."
    assert repository.get_by_id(created.id) == created


def test_create_consultation_keeps_question_and_category() -> None:
    service, _, _ = _make_service()

    created = service.create_consultation("Posso reciclar isopor?", "residuos")

    assert created.question == "Posso reciclar isopor?"
    assert created.category == "residuos"


def test_list_consultations_returns_all_from_repository() -> None:
    service, _, _ = _make_service()
    first = service.create_consultation("Pergunta 1", "residuos")
    second = service.create_consultation("Pergunta 2", "agua")

    results = service.list_consultations()

    assert {c.id for c in results} == {first.id, second.id}


def test_list_consultations_returns_empty_list_when_no_consultations() -> None:
    service, _, _ = _make_service()

    assert service.list_consultations() == []


def test_get_consultation_returns_existing_consultation() -> None:
    service, _, _ = _make_service()
    created = service.create_consultation("Pergunta", "residuos")

    assert service.get_consultation(created.id) == created


def test_get_consultation_returns_none_when_not_found() -> None:
    service, _, _ = _make_service()

    assert service.get_consultation("id-inexistente") is None


def test_delete_consultation_returns_true_when_removed() -> None:
    service, _, _ = _make_service()
    created = service.create_consultation("Pergunta", "residuos")

    assert service.delete_consultation(created.id) is True
    assert service.get_consultation(created.id) is None


def test_delete_consultation_returns_false_when_not_found() -> None:
    service, _, _ = _make_service()

    assert service.delete_consultation("id-inexistente") is False
