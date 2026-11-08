from __future__ import annotations

from abc import ABC, abstractmethod

from app.domain.models.user import Address, User


class UserRepository(ABC):
    """Contrato de persistência para User."""

    @abstractmethod
    def save(self, user: User) -> User:
        """Persiste um usuário e devolve o registro salvo."""
        raise NotImplementedError

    @abstractmethod
    def get_by_id(self, user_id: str) -> User | None:
        """Busca um usuário pelo id; retorna None se não existir."""
        raise NotImplementedError

    @abstractmethod
    def list_all(self, *, limit: int = 50, skip: int = 0) -> list[User]:
        """Lista usuários (mais recentes primeiro), com paginação opcional."""
        raise NotImplementedError

    @abstractmethod
    def add_address(self, user_id: str, address: Address) -> User | None:
        """Acrescenta um endereço ao usuário; retorna None se o usuário não existir."""
        raise NotImplementedError

    @abstractmethod
    def delete(self, user_id: str) -> bool:
        """Remove um usuário pelo id; retorna True se algo foi removido."""
        raise NotImplementedError
