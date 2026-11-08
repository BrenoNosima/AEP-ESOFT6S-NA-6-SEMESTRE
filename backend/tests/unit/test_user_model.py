from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from app.domain.models.user import Address, User

MARINGA = Address(street="Rua A, 100", city="Maringá", state="PR")
CURITIBA = Address(street="Rua B, 200", city="Curitiba", state="PR")


def test_user_starts_without_addresses() -> None:
    user = User(name="João", email="joao@email.com")

    assert user.addresses == ()
    assert user.primary_address() is None


def test_primary_address_is_the_first_one() -> None:
    user = User(name="João", email="joao@email.com", addresses=(MARINGA, CURITIBA))

    assert user.primary_address() == MARINGA


def test_with_address_returns_new_user_and_keeps_original_untouched() -> None:
    user = User(name="João", email="joao@email.com", addresses=(MARINGA,))

    updated = user.with_address(CURITIBA)

    assert updated.addresses == (MARINGA, CURITIBA)
    assert updated.id == user.id
    assert user.addresses == (MARINGA,)


def test_user_is_immutable() -> None:
    user = User(name="João", email="joao@email.com")

    with pytest.raises(FrozenInstanceError):
        user.name = "Maria"  # type: ignore[misc]


def test_each_user_gets_its_own_id_and_timezone_aware_created_at() -> None:
    first = User(name="João", email="joao@email.com")
    second = User(name="Maria", email="maria@email.com")

    assert first.id != second.id
    assert first.created_at.tzinfo is not None
    assert first.created_at.microsecond == 0
