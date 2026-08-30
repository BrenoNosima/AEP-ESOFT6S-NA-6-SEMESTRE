from app.domain.interfaces.llm_provider import LLMProvider
from app.services.sustainability_service import SustainabilityService


class FakeLLMProvider(LLMProvider):
    def __init__(self, fixed_response: str) -> None:
        self.fixed_response = fixed_response
        self.received_prompt: str | None = None

    def generate_response(self, prompt: str) -> str:
        self.received_prompt = prompt
        return self.fixed_response


def test_service_uses_provider_and_returns_its_response() -> None:
    expected_response = "Leve as pilhas a um ponto de coleta adequado."
    provider = FakeLLMProvider(expected_response)
    service = SustainabilityService(provider)

    response = service.generate_guidance("Como devo descartar pilhas usadas?")

    assert provider.received_prompt is not None
    assert response == expected_response


def test_user_question_is_included_in_prompt() -> None:
    question = "Como devo descartar pilhas usadas?"
    provider = FakeLLMProvider("Resposta sustentável.")
    service = SustainabilityService(provider)

    service.generate_guidance(question)

    assert provider.received_prompt is not None
    assert question in provider.received_prompt


def test_prompt_requests_sustainability_guidance() -> None:
    provider = FakeLLMProvider("Resposta sustentável.")
    service = SustainabilityService(provider)

    service.generate_guidance("O que fazer com óleo de cozinha usado?")

    assert provider.received_prompt is not None
    assert "sustentabilidade" in provider.received_prompt.lower()
    assert "orientações práticas" in provider.received_prompt.lower()
