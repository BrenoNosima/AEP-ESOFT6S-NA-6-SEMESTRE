from __future__ import annotations

import pytest

from app.api.schemas import ConsultationCategory
from app.domain.models.category import Category


def test_category_exposes_the_supported_values() -> None:
    assert [category.value for category in Category] == [
        "residuos",
        "agua",
        "energia",
        "consumo",
        "geral",
    ]


def test_category_is_built_from_its_string_value() -> None:
    assert Category("agua") is Category.agua
    assert Category.agua == "agua"


def test_category_rejects_unknown_value() -> None:
    with pytest.raises(ValueError):
        Category("xpto")


def test_api_schema_reuses_the_domain_category() -> None:
    assert ConsultationCategory is Category
