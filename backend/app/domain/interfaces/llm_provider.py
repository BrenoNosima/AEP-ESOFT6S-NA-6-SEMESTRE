from abc import ABC, abstractmethod


class LLMProvider(ABC):
    """Contrato para provedores de modelos de linguagem."""

    @abstractmethod
    def generate_response(self, prompt: str) -> str:
        """Gera uma resposta textual a partir de um prompt."""
        raise NotImplementedError
