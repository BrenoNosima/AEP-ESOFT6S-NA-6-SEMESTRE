"""Testes simples do contrato usado pelos provedores de linguagem.

Este arquivo testa somente regras locais. Assim, a suíte não precisa acessar a
internet, consumir créditos ou possuir uma chave da Groq.
"""

from app.domain.interfaces.llm_provider import LLMProvider
from app.llm.providers.groq_provider import GroqProvider


def test_groq_provider_segue_o_contrato_da_aplicacao() -> None:
    """Confere que o provider da Groq pertence ao contrato esperado."""
    assert issubclass(GroqProvider, LLMProvider)
