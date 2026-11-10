from __future__ import annotations

import logging
from collections.abc import Sequence

from app.domain.exceptions import NotFoundError
from app.domain.interfaces.consultation_repository import ConsultationRepository
from app.domain.interfaces.user_repository import UserRepository
from app.domain.models.consultation import Consultation
from app.domain.models.user import Address, User

logger = logging.getLogger(__name__)

_NOT_FOUND = "Usuário não encontrado."


class UserService:
    """Regras de negócio de usuários, incluindo a integridade com as consultas."""

    def __init__(
        self,
        users: UserRepository,
        consultations: ConsultationRepository,
    ) -> None:
        self._users = users
        self._consultations = consultations

    def create_user(
        self, name: str, email: str, addresses: Sequence[Address] = ()
    ) -> User:
        # E-mail duplicado: o repositório lança ConflictError (índice único).
        saved = self._users.save(User(name=name, email=email, addresses=tuple(addresses)))
        logger.info("usuário criado id=%s", saved.id)
        return saved

    def get_user(self, user_id: str) -> User:
        user = self._users.get_by_id(user_id)
        if user is None:
            raise NotFoundError(_NOT_FOUND)
        return user

    def list_users(self, *, limit: int = 50, skip: int = 0) -> list[User]:
        return self._users.list_all(limit=limit, skip=skip)

    def add_address(self, user_id: str, address: Address) -> User:
        updated = self._users.add_address(user_id, address)
        if updated is None:
            raise NotFoundError(_NOT_FOUND)
        logger.info("endereço adicionado id=%s cidade=%s", user_id, address.city)
        return updated

    def list_consultations(
        self, user_id: str, *, limit: int = 50, skip: int = 0
    ) -> list[Consultation]:
        """Histórico de consultas do usuário (mais recentes primeiro)."""
        self.get_user(user_id)
        return self._consultations.list_all(user_id=user_id, limit=limit, skip=skip)

    def summarize_consultations(self, user_id: str) -> dict[str, int]:
        """Total de consultas do usuário por categoria (agregação $group no MongoDB)."""
        self.get_user(user_id)
        return self._consultations.count_by_category(user_id)

    def delete_user(self, user_id: str) -> int:
        """Remove o usuário e, em cascata, as consultas dele.

        Retorna quantas consultas foram removidas. Sem transação no MongoDB, a
        ordem importa: as consultas saem antes do usuário, então uma falha no
        meio deixa no máximo um usuário sem consultas, nunca consultas órfãs.
        """
        self.get_user(user_id)
        removed = self._consultations.delete_by_user(user_id)
        self._users.delete(user_id)
        logger.info("usuário removido id=%s consultas_removidas=%s", user_id, removed)
        return removed
