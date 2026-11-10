from unittest.mock import MagicMock

import pytest

from app.api.services.sustainability_service import SustainabilityService
from app.domain.exceptions import LLMProviderError
from app.domain.interfaces.llm_provider import LLMProvider
from app.domain.models.category import Category
from app.llm.providers.fake_provider import FakeLLMProvider


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


def test_guidance_prompt_contains_city_and_state() -> None:
    question = "Onde posso descartar pilhas usadas?"
    provider = FakeLLMProvider("Consulte os canais oficiais do município.")
    service = SustainabilityService(provider)

    response = service.generate_guidance(
        question,
        city="Maringá",
        state="PR",
    )

    assert response == "Consulte os canais oficiais do município."
    assert provider.received_prompt is not None
    assert question in provider.received_prompt
    assert "Maringá" in provider.received_prompt
    assert "PR" in provider.received_prompt


def test_guidance_prompt_handles_missing_location() -> None:
    provider = FakeLLMProvider("Orientação sustentável.")
    service = SustainabilityService(provider)

    service.generate_guidance("Como reduzir o consumo de água?")

    assert provider.received_prompt is not None
    assert "localização do usuário não foi informada" in provider.received_prompt.lower()


def test_guidance_prompt_forbids_invented_local_information() -> None:
    provider = FakeLLMProvider("Orientação sustentável.")
    service = SustainabilityService(provider)

    service.generate_guidance(
        "Onde descarto óleo de cozinha?",
        city="Curitiba",
        state="PR",
    )

    assert provider.received_prompt is not None
    prompt = provider.received_prompt.lower()
    assert "não invente endereços" in prompt
    assert "pontos de coleta" in prompt
    assert "horários de atendimento" in prompt
    assert "regras municipais" in prompt
    assert "canais oficiais da prefeitura" in prompt


def test_generate_guidance_propagates_provider_error() -> None:
    provider = MagicMock(spec=LLMProvider)
    provider.generate_response.side_effect = LLMProviderError("Groq indisponível.")
    service = SustainabilityService(provider)

    with pytest.raises(LLMProviderError, match="Groq indisponível"):
        service.generate_guidance(
            "Onde descarto pilhas?",
            city="Maringá",
            state="PR",
        )


@pytest.mark.parametrize("category", list(Category))
def test_classify_category_accepts_every_supported_category(category: Category) -> None:
    provider = FakeLLMProvider(category.value)
    service = SustainabilityService(provider)

    result = service.classify_category("Como posso economizar recursos?")

    assert result is category


def test_classify_category_normalizes_whitespace_and_case() -> None:
    provider = FakeLLMProvider("  ReSiDuOs \n")
    service = SustainabilityService(provider)

    result = service.classify_category("Onde descarto pilhas usadas?")

    assert result is Category.residuos


def test_classification_prompt_contains_question_and_allowed_categories() -> None:
    question = "Como reduzir o consumo de energia em casa?"
    provider = FakeLLMProvider("energia")
    service = SustainabilityService(provider)

    service.classify_category(question)

    assert provider.received_prompt is not None
    assert question in provider.received_prompt
    for category in Category:
        assert category.value in provider.received_prompt
    assert "somente" in provider.received_prompt.lower()


def test_classify_category_rejects_unknown_category() -> None:
    provider = FakeLLMProvider("reciclagem")
    service = SustainabilityService(provider)

    with pytest.raises(LLMProviderError, match="categoria inválida"):
        service.classify_category("Onde descarto uma garrafa de vidro?")


def test_classify_category_rejects_non_string_response() -> None:
    provider = MagicMock(spec=LLMProvider)
    provider.generate_response.return_value = ["residuos"]
    service = SustainabilityService(provider)

    with pytest.raises(LLMProviderError, match="formato inválido"):
        service.classify_category("Onde descarto pilhas usadas?")


def test_classify_category_propagates_provider_error() -> None:
    provider = MagicMock(spec=LLMProvider)
    provider.generate_response.side_effect = LLMProviderError("Groq indisponível.")
    service = SustainabilityService(provider)

    with pytest.raises(LLMProviderError, match="Groq indisponível"):
        service.classify_category("Como economizar água?")
