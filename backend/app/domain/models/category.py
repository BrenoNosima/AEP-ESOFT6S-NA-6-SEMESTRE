from __future__ import annotations

from enum import Enum


class Category(str, Enum):
    """Categorias de consulta de sustentabilidade reconhecidas pelo domínio."""

    residuos = "residuos"
    agua = "agua"
    energia = "energia"
    consumo = "consumo"
    geral = "geral"
