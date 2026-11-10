from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Location:
    """Cidade/estado usados na resposta de uma consulta (snapshot do endereço do usuário)."""

    city: str
    state: str
