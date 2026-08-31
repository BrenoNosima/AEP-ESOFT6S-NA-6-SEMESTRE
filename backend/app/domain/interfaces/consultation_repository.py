from __future__ import annotations

from abc import ABC, abstractmethod

from app.domain.models.consultation import Consultation


class ConsultationRepository(ABC):
    """Contrato de persistência para Consultation."""

    @abstractmethod
    def save(self, consultation: Consultation) -> Consultation:
        """Persiste uma consulta e devolve o registro salvo."""
        raise NotImplementedError

    @abstractmethod
    def list_all(self) -> list[Consultation]:
        """Lista todas as consultas armazenadas."""
        raise NotImplementedError

    @abstractmethod
    def get_by_id(self, consultation_id: str) -> Consultation | None:
        """Busca uma consulta pelo id; retorna None se não existir."""
        raise NotImplementedError

    @abstractmethod
    def delete(self, consultation_id: str) -> bool:
        """Remove uma consulta pelo id; retorna True se algo foi removido."""
        raise NotImplementedError

    @abstractmethod
    def update_category(self, consultation_id: str, category: str) -> Consultation | None:
        """Atualiza a categoria de uma consulta existente; retorna None se não existir."""
        raise NotImplementedError
