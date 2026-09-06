from app.domain.interfaces.llm_provider import LLMProvider


class FakeLLMProvider(LLMProvider):
    """LLMProvider determinístico para testes: não chama API externa."""

    def __init__(self, fixed_response: str = "Leve o material a um ponto de coleta.") -> None:
        self.fixed_response = fixed_response
        self.received_prompt: str | None = None

    def generate_response(self, prompt: str) -> str:
        self.received_prompt = prompt
        return self.fixed_response
