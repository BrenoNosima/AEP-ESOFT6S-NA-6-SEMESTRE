from __future__ import annotations

from dataclasses import replace

import pytest
from fastapi.testclient import TestClient

from app.api.dependencies import get_consultation_service, get_llm_provider
from app.api.repositories.mongo_user_repository import MongoUserRepository
from app.api.services.consultation_service import ConsultationService
from app.api.services.sustainability_service import SustainabilityService
from app.domain.exceptions import ConflictError, LLMProviderError, RepositoryError
from app.domain.interfaces.consultation_repository import ConsultationRepository
from app.domain.interfaces.llm_provider import LLMProvider
from app.domain.models.consultation import Consultation
from app.llm.providers.fake_provider import FakeLLMProvider
from app.main import app


class InMemoryConsultationRepository(ConsultationRepository):
    def __init__(self) -> None:
        self._consultations: dict[str, Consultation] = {}

    def save(self, consultation: Consultation) -> Consultation:
        self._consultations[consultation.id] = consultation
        return consultation

    def list_all(
        self,
        *,
        category: str | None = None,
        user_id: str | None = None,
        limit: int = 50,
        skip: int = 0,
    ) -> list[Consultation]:
        items = sorted(
            self._consultations.values(), key=lambda c: c.created_at, reverse=True
        )
        if category is not None:
            items = [c for c in items if c.category == category]
        if user_id is not None:
            items = [c for c in items if c.user_id == user_id]
        return items[skip : skip + limit]

    def count_by_category(self, user_id: str) -> dict[str, int]:
        counts: dict[str, int] = {}
        for c in self._consultations.values():
            if c.user_id == user_id:
                counts[c.category] = counts.get(c.category, 0) + 1
        return counts

    def get_by_id(self, consultation_id: str) -> Consultation | None:
        return self._consultations.get(consultation_id)

    def delete(self, consultation_id: str) -> bool:
        return self._consultations.pop(consultation_id, None) is not None

    def delete_by_user(self, user_id: str) -> int:
        return 0

    def update_category(self, consultation_id: str, category: str) -> Consultation | None:
        existing = self._consultations.get(consultation_id)
        if existing is None:
            return None
        updated = replace(existing, category=category)
        self._consultations[consultation_id] = updated
        return updated


class FailingConsultationRepository(InMemoryConsultationRepository):
    def list_all(self, **_: object) -> list[Consultation]:
        raise RepositoryError("MongoDB indisponível")


class ConflictingConsultationRepository(InMemoryConsultationRepository):
    def save(self, consultation: Consultation) -> Consultation:
        raise ConflictError("Registro duplicado.")


class ScriptedLLMProvider(LLMProvider):
    """Devolve as respostas na ordem dada (1ª: classificação, 2ª: orientação)."""

    def __init__(self, *responses: str) -> None:
        self._responses = list(responses)

    def generate_response(self, prompt: str) -> str:
        return self._responses.pop(0)


class FailingLLMProvider(LLMProvider):
    def generate_response(self, prompt: str) -> str:
        raise LLMProviderError("Não foi possível obter uma resposta da Groq.")


@pytest.fixture
def user(client: TestClient) -> dict:
    response = client.post(
        "/users",
        json={
            "name": "Ana Souza",
            "email": "ana@example.com",
            "addresses": [{"street": "Rua das Flores, 100", "city": "Maringá", "state": "PR"}],
        },
    )
    assert response.status_code == 201
    return response.json()


def _post(client: TestClient, user: dict, question: str, category: str | None = "geral"):
    payload = {"user_id": user["id"], "question": question}
    if category is not None:
        payload["category"] = category
    return client.post("/consultations", json=payload)


def _create(client: TestClient, user: dict, question: str, category: str) -> dict:
    return _post(client, user, question, category).json()


def _service_with(test_database, repository: ConsultationRepository) -> ConsultationService:
    return ConsultationService(
        SustainabilityService(FakeLLMProvider("x")),
        repository,
        MongoUserRepository(test_database),
    )


def test_health_returns_ok(client: TestClient) -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_create_consultation_returns_201_with_generated_answer(
    client: TestClient, user: dict
) -> None:
    response = _post(client, user, "Posso jogar óleo na pia?", "residuos")

    assert response.status_code == 201
    body = response.json()
    assert body["question"] == "Posso jogar óleo na pia?"
    assert body["category"] == "residuos"
    assert body["answer"] == "Descarte em ponto de coleta."
    assert body["user_id"] == user["id"]
    assert body["location"] == {"city": "Maringá", "state": "PR"}
    assert "id" in body and "created_at" in body


def test_create_consultation_classifies_category_when_omitted(
    client: TestClient, user: dict
) -> None:
    app.dependency_overrides[get_llm_provider] = lambda: ScriptedLLMProvider(
        "agua", "Feche a torneira ao escovar os dentes."
    )

    response = _post(client, user, "Como economizar água em casa?", category=None)

    assert response.status_code == 201
    assert response.json()["category"] == "agua"
    assert response.json()["answer"] == "Feche a torneira ao escovar os dentes."


def test_create_consultation_returns_404_when_user_missing(client: TestClient) -> None:
    response = client.post(
        "/consultations",
        json={"user_id": "id-inexistente", "question": "Posso jogar óleo na pia?"},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Usuário não encontrado."}


def test_create_consultation_requires_user_id(client: TestClient) -> None:
    response = client.post(
        "/consultations", json={"question": "Posso jogar óleo na pia?", "category": "agua"}
    )

    assert response.status_code == 422


def test_created_consultation_shows_in_user_history_and_summary(
    client: TestClient, user: dict
) -> None:
    created = _create(client, user, "Como economizar água?", "agua")

    history = client.get(f"/users/{user['id']}/consultations").json()
    summary = client.get(f"/users/{user['id']}/consultations/summary").json()

    assert [c["id"] for c in history] == [created["id"]]
    assert summary["by_category"] == [{"category": "agua", "total": 1}]


def test_create_consultation_rejects_short_question(client: TestClient, user: dict) -> None:
    response = _post(client, user, "oi", "residuos")

    assert response.status_code == 422


def test_create_consultation_rejects_unknown_category(client: TestClient, user: dict) -> None:
    response = _post(client, user, "Como descarto pilhas?", "xpto")

    assert response.status_code == 422


def test_list_consultations_returns_created_items(client: TestClient, user: dict) -> None:
    created = _create(client, user, "Como economizar água?", "agua")

    response = client.get("/consultations")

    assert response.status_code == 200
    assert any(item["id"] == created["id"] for item in response.json())


def test_list_consultations_filters_by_category(client: TestClient, user: dict) -> None:
    _create(client, user, "Como economizar água em casa?", "agua")
    _create(client, user, "Como descartar pilhas usadas?", "residuos")

    response = client.get("/consultations", params={"category": "agua"})

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["category"] == "agua"


def test_list_consultations_respects_limit(client: TestClient, user: dict) -> None:
    for i in range(3):
        _create(client, user, f"Pergunta numero {i}", "geral")

    response = client.get("/consultations", params={"limit": 2})

    assert response.status_code == 200
    assert len(response.json()) == 2


def test_get_consultation_by_id_returns_it(client: TestClient, user: dict) -> None:
    created = _create(client, user, "Como descartar pilhas?", "residuos")

    response = client.get(f"/consultations/{created['id']}")

    assert response.status_code == 200
    assert response.json()["id"] == created["id"]


def test_get_consultation_by_id_returns_404_when_missing(client: TestClient) -> None:
    response = client.get("/consultations/id-inexistente")

    assert response.status_code == 404
    assert response.json() == {"detail": "Consulta não encontrada."}


def test_patch_category_updates_it(client: TestClient, user: dict) -> None:
    created = _create(client, user, "Como separar lixo reciclável?", "geral")

    response = client.patch(
        f"/consultations/{created['id']}", json={"category": "residuos"}
    )

    assert response.status_code == 200
    assert response.json()["category"] == "residuos"
    assert client.get(f"/consultations/{created['id']}").json()["category"] == "residuos"


def test_patch_category_returns_404_when_missing(client: TestClient) -> None:
    response = client.patch(
        "/consultations/id-inexistente", json={"category": "agua"}
    )

    assert response.status_code == 404


def test_delete_consultation_returns_204(client: TestClient, user: dict) -> None:
    created = _create(client, user, "Como reduzir consumo de energia?", "energia")

    response = client.delete(f"/consultations/{created['id']}")

    assert response.status_code == 204
    assert client.get(f"/consultations/{created['id']}").status_code == 404


def test_delete_consultation_returns_404_when_missing(client: TestClient) -> None:
    response = client.delete("/consultations/id-inexistente")

    assert response.status_code == 404


def test_list_consultations_returns_503_when_repository_unavailable(
    client: TestClient, test_database
) -> None:
    def _override_failing() -> ConsultationService:
        return _service_with(test_database, FailingConsultationRepository())

    app.dependency_overrides[get_consultation_service] = _override_failing
    try:
        response = client.get("/consultations")
    finally:
        del app.dependency_overrides[get_consultation_service]

    assert response.status_code == 503
    assert response.json() == {"detail": "Serviço de dados indisponível. Tente novamente."}


def test_create_consultation_returns_502_when_llm_fails(client: TestClient, user: dict) -> None:
    app.dependency_overrides[get_llm_provider] = FailingLLMProvider

    response = _post(client, user, "Posso jogar óleo na pia?", "residuos")

    assert response.status_code == 502
    assert response.json() == {"detail": "Não foi possível obter uma resposta da Groq."}
    assert client.get("/consultations").json() == []


def test_conflict_error_is_translated_to_409(
    client: TestClient, user: dict, test_database
) -> None:
    def _override_conflicting() -> ConsultationService:
        return _service_with(test_database, ConflictingConsultationRepository())

    app.dependency_overrides[get_consultation_service] = _override_conflicting
    try:
        response = _post(client, user, "Posso jogar óleo na pia?", "residuos")
    finally:
        del app.dependency_overrides[get_consultation_service]

    assert response.status_code == 409
    assert response.json() == {"detail": "Registro duplicado."}
