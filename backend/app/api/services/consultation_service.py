from __future__ import annotations

import logging

from app.domain.interfaces.consultation_repository import ConsultationRepository
from app.domain.models.consultation import Consultation
from app.api.services.sustainability_service import SustainabilityService

logger = logging.getLogger(__name__)


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
        saved = self._repository.save(consultation)
        logger.info("consulta criada id=%s categoria=%s", saved.id, saved.category)
        return saved

    def list_consultations(
        self,
        *,
        category: str | None = None,
        limit: int = 50,
        skip: int = 0,
    ) -> list[Consultation]:
        return self._repository.list_all(category=category, limit=limit, skip=skip)

    def get_consultation(self, consultation_id: str) -> Consultation | None:
        return self._repository.get_by_id(consultation_id)

    def update_consultation_category(
        self, consultation_id: str, category: str
    ) -> Consultation | None:
        updated = self._repository.update_category(consultation_id, category)
        if updated is not None:
            logger.info(
                "categoria atualizada id=%s categoria=%s", updated.id, updated.category
            )
        return updated

    def delete_consultation(self, consultation_id: str) -> bool:
        deleted = self._repository.delete(consultation_id)
        if deleted:
            logger.info("consulta removida id=%s", consultation_id)
        return deleted
