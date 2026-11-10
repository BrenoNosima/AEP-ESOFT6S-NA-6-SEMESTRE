from __future__ import annotations

from fastapi.testclient import TestClient

from app.api.dependencies import get_llm_provider
from app.domain.interfaces.llm_provider import LLMProvider
from app.main import app


class ScriptedLLMProvider(LLMProvider):
    def __init__(self, *responses: str) -> None:
        self._responses = list(responses)
        self.prompts: list[str] = []

    def generate_response(self, prompt: str) -> str:
        self.prompts.append(prompt)
        return self._responses.pop(0)


def test_complete_user_consultation_flow(client: TestClient) -> None:
    user_response = client.post(
        "/users",
        json={
            "name": "Ana Souza",
            "email": "ana@example.com",
            "addresses": [
                {
                    "street": "Rua das Flores, 100",
                    "city": "Maringá",
                    "state": "PR",
                }
            ],
        },
    )
    assert user_response.status_code == 201
    user = user_response.json()

    provider = ScriptedLLMProvider(
        "residuos",
        "Leve as pilhas a um ponto de coleta indicado pelos canais oficiais.",
    )
    app.dependency_overrides[get_llm_provider] = lambda: provider

    consultation_response = client.post(
        "/consultations",
        json={
            "user_id": user["id"],
            "question": "Onde devo descartar pilhas usadas?",
        },
    )
    assert consultation_response.status_code == 201
    consultation = consultation_response.json()
    assert consultation["user_id"] == user["id"]
    assert consultation["category"] == "residuos"
    assert consultation["location"] == {"city": "Maringá", "state": "PR"}
    assert consultation["answer"] == (
        "Leve as pilhas a um ponto de coleta indicado pelos canais oficiais."
    )
    assert len(provider.prompts) == 2
    assert "Onde devo descartar pilhas usadas?" in provider.prompts[0]
    assert "Maringá" in provider.prompts[1]
    assert "PR" in provider.prompts[1]

    history_response = client.get(f"/users/{user['id']}/consultations")
    assert history_response.status_code == 200
    assert [item["id"] for item in history_response.json()] == [consultation["id"]]

    summary_response = client.get(f"/users/{user['id']}/consultations/summary")
    assert summary_response.status_code == 200
    assert summary_response.json() == {
        "user_id": user["id"],
        "total": 1,
        "by_category": [{"category": "residuos", "total": 1}],
    }

    delete_response = client.delete(f"/users/{user['id']}")
    assert delete_response.status_code == 204
    assert client.get(f"/users/{user['id']}").status_code == 404
    assert client.get(f"/consultations/{consultation['id']}").status_code == 404
