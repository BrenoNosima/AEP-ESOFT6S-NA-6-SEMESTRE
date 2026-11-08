from __future__ import annotations

import pytest
from pymongo.errors import PyMongoError, ServerSelectionTimeoutError

from app.api.repositories._mongo_errors import translate_errors
from app.domain.exceptions import RepositoryError


def test_translate_errors_returns_the_wrapped_result() -> None:
    @translate_errors
    def ok(value: int) -> int:
        return value * 2

    assert ok(21) == 42


def test_translate_errors_converts_pymongo_error_into_repository_error() -> None:
    @translate_errors
    def failing() -> None:
        raise ServerSelectionTimeoutError("mongo fora do ar")

    with pytest.raises(RepositoryError) as error:
        failing()

    assert isinstance(error.value.__cause__, PyMongoError)


def test_translate_errors_lets_non_mongo_errors_pass_through() -> None:
    @translate_errors
    def failing() -> None:
        raise ValueError("erro de regra")

    with pytest.raises(ValueError):
        failing()


def test_translate_errors_keeps_the_wrapped_function_name() -> None:
    @translate_errors
    def save() -> None:
        return None

    assert save.__name__ == "save"
