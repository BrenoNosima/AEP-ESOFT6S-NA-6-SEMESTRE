from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import uuid4

from app.domain.models.location import Location


@dataclass(frozen=True)
class Consultation:
    """Registro de uma consulta de sustentabilidade já respondida.

    `user_id` referencia `users._id` e `location` é um snapshot do endereço usado
    na resposta. Ambos são opcionais para ler documentos da 1ª entrega.
    """

    question: str
    category: str
    answer: str
    id: str = field(default_factory=lambda: str(uuid4()))
    # microsecond=0: BSON guarda datetime só em milissegundo; mantém save/get idempotente.
    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc).replace(microsecond=0)
    )
    user_id: str | None = None
    location: Location | None = None
