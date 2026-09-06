from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from app.llm.providers.groq_provider import GroqProvider


@patch("app.llm.providers.groq_provider.ChatGroq")
def test_generate_response_returns_the_client_content(chat_groq_class: MagicMock) -> None:
    mock_client = MagicMock()
    mock_client.invoke.return_value = MagicMock(content="Leve a um ponto de coleta.")
    chat_groq_class.return_value = mock_client

    provider = GroqProvider(api_key="fake-key")
    response = provider.generate_response("Como descarto pilhas usadas?")

    assert response == "Leve a um ponto de coleta."
    mock_client.invoke.assert_called_once_with("Como descarto pilhas usadas?")


@patch("app.llm.providers.groq_provider.ChatGroq")
def test_generate_response_wraps_client_errors_in_runtime_error(chat_groq_class: MagicMock) -> None:
    mock_client = MagicMock()
    mock_client.invoke.side_effect = TimeoutError("a Groq não respondeu a tempo")
    chat_groq_class.return_value = mock_client

    provider = GroqProvider(api_key="fake-key")

    with pytest.raises(RuntimeError, match="Não foi possível obter uma resposta da Groq."):
        provider.generate_response("Como descarto pilhas usadas?")


@patch("app.llm.providers.groq_provider.ChatGroq")
def test_generate_response_rejects_non_string_content(chat_groq_class: MagicMock) -> None:
    mock_client = MagicMock()
    mock_client.invoke.return_value = MagicMock(content=["resposta", "em", "lista"])
    chat_groq_class.return_value = mock_client

    provider = GroqProvider(api_key="fake-key")

    with pytest.raises(RuntimeError, match="formato inválido"):
        provider.generate_response("Como descarto pilhas usadas?")


@patch("app.llm.providers.groq_provider.ChatGroq")
def test_init_wraps_client_construction_errors(chat_groq_class: MagicMock) -> None:
    chat_groq_class.side_effect = ValueError("sem api key")

    with pytest.raises(RuntimeError, match="inicializar o cliente da Groq"):
        GroqProvider(api_key="")


@patch("app.llm.providers.groq_provider.ChatGroq")
def test_generate_response_rejects_empty_content(chat_groq_class: MagicMock) -> None:
    mock_client = MagicMock()
    mock_client.invoke.return_value = MagicMock(content="   ")
    chat_groq_class.return_value = mock_client

    provider = GroqProvider(api_key="fake-key")

    with pytest.raises(RuntimeError, match="resposta vazia"):
        provider.generate_response("Como descarto pilhas usadas?")


@patch("app.llm.providers.groq_provider.ChatGroq")
def test_init_forwards_timeout_and_retries(chat_groq_class: MagicMock) -> None:
    GroqProvider(api_key="fake-key", timeout=12.0, max_retries=5)

    _, kwargs = chat_groq_class.call_args
    assert kwargs["timeout"] == 12.0
    assert kwargs["max_retries"] == 5
