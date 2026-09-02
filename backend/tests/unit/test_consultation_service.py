from app.domain.interfaces.consultation_repository import ConsultationRepository
from app.domain.interfaces.llm_provider import LLMProvider
from app.domain.models.consultation import Consultation
from app.services.consultation_service import ConsultationService
from app.services.sustainability_service import SustainabilityService


class FakeLLMProvider(LLMProvider):
    def __init__(self, fixed_response: str) -> None:
        self.fixed_response = fixed_response

    def generate_response(self, prompt: str) -> str:
        return self.fixed_response


class InMemoryConsultationRepository(ConsultationRepository):
    def __init__(self) -> None:
        self._consultations: dict[str, Consultation] = {}

    def save(self, consultation: Consultation) -> Consultation:
        self._consultations[consultation.id] = consultation
        return consultation

    def list_all(self) -> list[Consultation]:
        return list(self._consultations.values())

    def get_by_id(self, consultation_id: str) -> Consultation | None:
        return self._consultations.get(consultation_id)

    def delete(self, consultation_id: str) -> bool:
        return self._consultations.pop(consultation_id, None) is not None

    def update_category(self, consultation_id: str, category: str) -> Consultation | None:
        existing = self._consultations.get(consultation_id)
        if existing is None:
            return None
        updated = Consultation(
            question=existing.question,
            category=category,
            answer=existing.answer,
            id=existing.id,
            created_at=existing.created_at,
        )
        self._consultations[updated.id] = updated
        return updated


def _build_service() -> tuple[ConsultationService, InMemoryConsultationRepository]:
    sustainability_service = SustainabilityService(FakeLLMProvider("Descarte em ponto de coleta."))
    repository = InMemoryConsultationRepository()
    return ConsultationService(sustainability_service, repository), repository


def test_create_consultation_generates_answer_and_persists() -> None:
    service, repository = _build_service()

    consultation = service.create_consultation("Posso jogar óleo na pia?", "residuos")

    assert consultation.question == "Posso jogar óleo na pia?"
    assert consultation.category == "residuos"
    assert consultation.answer == "Descarte em ponto de coleta."
    assert repository.get_by_id(consultation.id) == consultation


def test_list_consultations_returns_all_from_repository() -> None:
    service, _ = _build_service()
    first = service.create_consultation("Como economizar água?", "agua")
    second = service.create_consultation("Como descartar pilhas?", "residuos")

    consultations = service.list_consultations()

    assert consultations == [first, second]


def test_get_consultation_returns_existing_and_none_otherwise() -> None:
    service, _ = _build_service()
    created = service.create_consultation("Como economizar energia?", "energia")

    assert service.get_consultation(created.id) == created
    assert service.get_consultation("id-inexistente") is None


def test_delete_consultation_returns_bool_from_repository() -> None:
    service, _ = _build_service()
    created = service.create_consultation("Como reduzir consumo?", "consumo")

    assert service.delete_consultation(created.id) is True
    assert service.delete_consultation(created.id) is False
