from __future__ import annotations

import mongomock
import pytest
from fastapi.testclient import TestClient

from app.api.router import get_consultation_service, get_llm_provider
from app.api.services.consultation_service import ConsultationService
from app.api.services.sustainability_service import SustainabilityService
from app.database.mongodb import get_database
from app.domain.exceptions import RepositoryError
from app.domain.interfaces.consultation_repository import ConsultationRepository
from app.domain.interfaces.llm_provider import LLMProvider
from app.domain.models.consultation import Consultation
from app.main import app


class FakeLLMProvider(LLMProvider):
    def __init__(self, fixed_response: str) -> None:
        self.fixed_response = fixed_response

    def generate_response(self, prompt: str) -> str:
        return self.fixed_response


class InMemoryConsultationRepository(ConsultationRepository):
    def __init__(self) -> None:
        self._consultations: dict[str, Consultation] = {}

    def save(self, consultation: Consultation) -> Consultation:
        self._consultations[consultation.id] = consultation
        return consultation

    def list_all(self) -> list[Consultation]:
        return list(self._consultations.values())

    def get_by_id(self, consultation_id: str) -> Consultation | None:
        return self._consultations.get(consultation_id)

    def delete(self, consultation_id: str) -> bool:
        return self._consultations.pop(consultation_id, None) is not None

    def update_category(self, consultation_id: str, category: str) -> Consultation | None:
        raise NotImplementedError


class FailingConsultationRepository(InMemoryConsultationRepository):
    def list_all(self) -> list[Consultation]:
        raise RepositoryError("MongoDB indisponível")


@pytest.fixture
def test_database():
    return mongomock.MongoClient().db


@pytest.fixture
def client(test_database) -> TestClient:
    app.dependency_overrides[get_llm_provider] = lambda: FakeLLMProvider(
        "Descarte em ponto de coleta."
    )
    app.dependency_overrides[get_database] = lambda: test_database

    yield TestClient(app)

    app.dependency_overrides.clear()


def test_health_returns_ok(client: TestClient) -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_create_consultation_returns_201_with_generated_answer(client: TestClient) -> None:
    response = client.post(
        "/consultations",
        json={"question": "Posso jogar óleo na pia?", "category": "residuos"},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["question"] == "Posso jogar óleo na pia?"
    assert body["category"] == "residuos"
    assert body["answer"] == "Descarte em ponto de coleta."
    assert "id" in body and "created_at" in body


def test_list_consultations_returns_created_items(client: TestClient) -> None:
    created = client.post(
        "/consultations",
        json={"question": "Como economizar água?", "category": "agua"},
    ).json()

    response = client.get("/consultations")

    assert response.status_code == 200
    assert any(item["id"] == created["id"] for item in response.json())


def test_get_consultation_by_id_returns_it(client: TestClient) -> None:
    created = client.post(
        "/consultations",
        json={"question": "Como descartar pilhas?", "category": "residuos"},
    ).json()

    response = client.get(f"/consultations/{created['id']}")

    assert response.status_code == 200
    assert response.json()["id"] == created["id"]


def test_get_consultation_by_id_returns_404_when_missing(client: TestClient) -> None:
    response = client.get("/consultations/id-inexistente")

    assert response.status_code == 404


def test_delete_consultation_returns_204(client: TestClient) -> None:
    created = client.post(
        "/consultations",
        json={"question": "Como reduzir consumo?", "category": "consumo"},
    ).json()

    response = client.delete(f"/consultations/{created['id']}")

    assert response.status_code == 204
    assert client.get(f"/consultations/{created['id']}").status_code == 404


def test_delete_consultation_returns_404_when_missing(client: TestClient) -> None:
    response = client.delete("/consultations/id-inexistente")

    assert response.status_code == 404


def test_list_consultations_returns_503_when_repository_unavailable(client: TestClient) -> None:
    def _override_failing() -> ConsultationService:
        return ConsultationService(
            SustainabilityService(FakeLLMProvider("x")), FailingConsultationRepository()
        )

    app.dependency_overrides[get_consultation_service] = _override_failing
    try:
        assert client.get("/consultations").status_code == 503
    finally:
        del app.dependency_overrides[get_consultation_service]
