from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import uuid4


@dataclass(frozen=True)
class Consultation:
    """Registro de uma consulta de sustentabilidade já respondida."""

    question: str
    category: str
    answer: str
    id: str = field(default_factory=lambda: str(uuid4()))
    # microsecond=0: BSON guarda datetime só em milissegundo; mantém save/get idempotente.
    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc).replace(microsecond=0)
    )
