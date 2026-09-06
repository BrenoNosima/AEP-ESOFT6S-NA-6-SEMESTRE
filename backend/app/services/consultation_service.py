from __future__ import annotations

from app.domain.interfaces.consultation_repository import ConsultationRepository
from app.domain.models.consultation import Consultation
from app.services.sustainability_service import SustainabilityService


class ConsultationService:
    def __init__(
        self,
        sustainability_service: SustainabilityService,
        repository: ConsultationRepository,
    ) -> None:
        self._sustainability_service = sustainability_service
        self._repository = repository

    def create_consultation(self, question: str, category: str) -> Consultation:
        answer = self._sustainability_service.generate_guidance(question)
        consultation = Consultation(question=question, category=category, answer=answer)
        return self._repository.save(consultation)

    def list_consultations(self) -> list[Consultation]:
        return self._repository.list_all()

    def get_consultation(self, consultation_id: str) -> Consultation | None:
        return self._repository.get_by_id(consultation_id)

    def delete_consultation(self, consultation_id: str) -> bool:
        return self._repository.delete(consultation_id)
