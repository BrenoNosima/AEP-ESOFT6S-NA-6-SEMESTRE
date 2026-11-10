from __future__ import annotations

import logging

from app.domain.exceptions import NotFoundError
from app.domain.interfaces.consultation_repository import ConsultationRepository
from app.domain.interfaces.user_repository import UserRepository
from app.domain.models.consultation import Consultation
from app.domain.models.location import Location
from app.api.services.sustainability_service import SustainabilityService

logger = logging.getLogger(__name__)

_NOT_FOUND = "Consulta não encontrada."
_USER_NOT_FOUND = "Usuário não encontrado."


class ConsultationService:
    def __init__(
        self,
        sustainability_service: SustainabilityService,
        repository: ConsultationRepository,
        users: UserRepository,
    ) -> None:
        self._sustainability_service = sustainability_service
        self._repository = repository
        self._users = users

    def create_consultation(
        self, user_id: str, question: str, category: str | None = None
    ) -> Consultation:
        """Gera e salva a orientação para a dúvida de um usuário existente.

        O usuário é buscado antes de qualquer chamada à LLM (404 sem custo).
        Sem categoria, a LLM classifica a pergunta. O endereço principal do
        usuário contextualiza a resposta e fica salvo como snapshot (`location`).
        """
        user = self._users.get_by_id(user_id)
        if user is None:
            raise NotFoundError(_USER_NOT_FOUND)

        classified = category is None
        if classified:
            category = self._sustainability_service.classify_category(question).value

        address = user.primary_address()
        location = Location(city=address.city, state=address.state) if address else None
        answer = self._sustainability_service.generate_guidance(
            question,
            city=location.city if location else None,
            state=location.state if location else None,
        )

        saved = self._repository.save(
            Consultation(
                question=question,
                category=category,
                answer=answer,
                user_id=user.id,
                location=location,
            )
        )
        logger.info(
            "consulta criada id=%s user_id=%s categoria=%s classificada=%s",
            saved.id,
            user.id,
            saved.category,
            classified,
        )
        return saved

    def list_consultations(
        self,
        *,
        category: str | None = None,
        limit: int = 50,
        skip: int = 0,
    ) -> list[Consultation]:
        return self._repository.list_all(category=category, limit=limit, skip=skip)

    def get_consultation(self, consultation_id: str) -> Consultation:
        consultation = self._repository.get_by_id(consultation_id)
        if consultation is None:
            raise NotFoundError(_NOT_FOUND)
        return consultation

    def update_consultation_category(
        self, consultation_id: str, category: str
    ) -> Consultation:
        updated = self._repository.update_category(consultation_id, category)
        if updated is None:
            raise NotFoundError(_NOT_FOUND)
        logger.info(
            "categoria atualizada id=%s categoria=%s", updated.id, updated.category
        )
        return updated

    def delete_consultation(self, consultation_id: str) -> None:
        if not self._repository.delete(consultation_id):
            raise NotFoundError(_NOT_FOUND)
        logger.info("consulta removida id=%s", consultation_id)
