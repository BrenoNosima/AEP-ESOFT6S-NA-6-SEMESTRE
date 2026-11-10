from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.api.repositories.mongo_consultation_repository import MongoConsultationRepository
from app.domain.models.consultation import Consultation

_HOME = {"street": "Rua das Flores, 100", "city": "Maringá", "state": "PR"}
_WORK = {"street": "Av. Brasil, 500", "city": "Curitiba", "state": "PR"}


@pytest.fixture
def consultations(test_database) -> MongoConsultationRepository:
    return MongoConsultationRepository(test_database)


def _create_user(client: TestClient, email: str = "ana@example.com", **extra) -> dict:
    payload = {"name": "Ana Souza", "email": email, "addresses": [_HOME], **extra}
    response = client.post("/users", json=payload)
    assert response.status_code == 201, response.text
    return response.json()


def _add_consultation(
    repository: MongoConsultationRepository, user_id: str, category: str
) -> Consultation:
    return repository.save(
        Consultation(question="Pergunta", category=category, answer="Resposta", user_id=user_id)
    )


def test_create_user_returns_201_with_normalized_fields(client: TestClient) -> None:
    response = client.post(
        "/users",
        json={
            "name": "  Ana Souza ",
            "email": " Ana@Example.COM ",
            "addresses": [{**_HOME, "state": "pr"}],
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["name"] == "Ana Souza"
    assert body["email"] == "ana@example.com"
    assert body["addresses"] == [_HOME]
    assert "id" in body and "created_at" in body


def test_create_user_without_addresses(client: TestClient) -> None:
    response = client.post("/users", json={"name": "Ana", "email": "ana@example.com"})

    assert response.status_code == 201
    assert response.json()["addresses"] == []


def test_create_user_returns_409_on_duplicate_email(client: TestClient) -> None:
    _create_user(client)

    response = client.post(
        "/users", json={"name": "Outra Ana", "email": "ANA@example.com"}
    )

    assert response.status_code == 409
    assert response.json() == {"detail": "E-mail já cadastrado."}


@pytest.mark.parametrize(
    "payload",
    [
        {"name": "Ana", "email": "sem-arroba"},
        {"name": "A", "email": "ana@example.com"},
        {"name": "Ana", "email": "ana@example.com", "addresses": [{**_HOME, "state": "Paraná"}]},
        {"name": "Ana", "email": "ana@example.com", "addresses": [{**_HOME, "city": " "}]},
    ],
)
def test_create_user_rejects_invalid_payload(client: TestClient, payload: dict) -> None:
    assert client.post("/users", json=payload).status_code == 422


def test_list_users_paginates(client: TestClient) -> None:
    for i in range(3):
        _create_user(client, email=f"u{i}@example.com")

    assert len(client.get("/users").json()) == 3
    assert len(client.get("/users", params={"limit": 2}).json()) == 2
    assert len(client.get("/users", params={"skip": 2}).json()) == 1


def test_get_user_returns_it(client: TestClient) -> None:
    created = _create_user(client)

    response = client.get(f"/users/{created['id']}")

    assert response.status_code == 200
    assert response.json() == created


def test_get_user_returns_404_when_missing(client: TestClient) -> None:
    response = client.get("/users/id-inexistente")

    assert response.status_code == 404
    assert response.json() == {"detail": "Usuário não encontrado."}


def test_add_address_appends_it(client: TestClient) -> None:
    created = _create_user(client)

    response = client.post(f"/users/{created['id']}/addresses", json=_WORK)

    assert response.status_code == 201
    assert response.json()["addresses"] == [_HOME, _WORK]
    assert client.get(f"/users/{created['id']}").json()["addresses"] == [_HOME, _WORK]


def test_add_address_returns_404_when_user_missing(client: TestClient) -> None:
    assert client.post("/users/id-inexistente/addresses", json=_WORK).status_code == 404


def test_delete_user_removes_user_and_their_consultations(
    client: TestClient, consultations: MongoConsultationRepository
) -> None:
    ana = _create_user(client)
    bia = _create_user(client, email="bia@example.com")
    _add_consultation(consultations, ana["id"], "agua")
    kept = _add_consultation(consultations, bia["id"], "agua")

    response = client.delete(f"/users/{ana['id']}")

    assert response.status_code == 204
    assert client.get(f"/users/{ana['id']}").status_code == 404
    assert consultations.list_all(user_id=ana["id"]) == []
    assert consultations.list_all(user_id=bia["id"]) == [kept]


def test_delete_user_returns_404_when_missing(client: TestClient) -> None:
    assert client.delete("/users/id-inexistente").status_code == 404


def test_user_history_lists_only_their_consultations(
    client: TestClient, consultations: MongoConsultationRepository
) -> None:
    ana = _create_user(client)
    bia = _create_user(client, email="bia@example.com")
    mine = [_add_consultation(consultations, ana["id"], "agua") for _ in range(2)]
    _add_consultation(consultations, bia["id"], "residuos")

    response = client.get(f"/users/{ana['id']}/consultations")

    assert response.status_code == 200
    assert {c["id"] for c in response.json()} == {c.id for c in mine}
    limited = client.get(f"/users/{ana['id']}/consultations", params={"limit": 1})
    assert len(limited.json()) == 1


def test_user_history_returns_404_when_user_missing(client: TestClient) -> None:
    assert client.get("/users/id-inexistente/consultations").status_code == 404


def test_user_summary_groups_by_category(
    client: TestClient, consultations: MongoConsultationRepository
) -> None:
    ana = _create_user(client)
    for category in ["agua", "agua", "residuos"]:
        _add_consultation(consultations, ana["id"], category)

    response = client.get(f"/users/{ana['id']}/consultations/summary")

    assert response.status_code == 200
    assert response.json() == {
        "user_id": ana["id"],
        "total": 3,
        "by_category": [
            {"category": "agua", "total": 2},
            {"category": "residuos", "total": 1},
        ],
    }


def test_user_summary_is_empty_without_consultations(client: TestClient) -> None:
    ana = _create_user(client)

    response = client.get(f"/users/{ana['id']}/consultations/summary")

    assert response.json() == {"user_id": ana["id"], "total": 0, "by_category": []}


def test_user_summary_returns_404_when_user_missing(client: TestClient) -> None:
    assert client.get("/users/id-inexistente/consultations/summary").status_code == 404
