from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import datetime, timezone
from uuid import uuid4


@dataclass(frozen=True)
class Address:
    """Endereço do usuário; embutido no documento do usuário (subdocumento)."""

    street: str
    city: str
    state: str


@dataclass(frozen=True)
class User:
    """Pessoa que faz consultas; dona de uma lista de endereços."""

    name: str
    email: str
    addresses: tuple[Address, ...] = ()
    id: str = field(default_factory=lambda: str(uuid4()))
    # microsecond=0: BSON guarda datetime só em milissegundo; mantém save/get idempotente.
    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc).replace(microsecond=0)
    )

    def primary_address(self) -> Address | None:
        """Primeiro endereço cadastrado, usado para contextualizar as orientações."""
        return self.addresses[0] if self.addresses else None

    def with_address(self, address: Address) -> User:
        """Nova instância com o endereço acrescentado (a entidade é imutável)."""
        return replace(self, addresses=(*self.addresses, address))
