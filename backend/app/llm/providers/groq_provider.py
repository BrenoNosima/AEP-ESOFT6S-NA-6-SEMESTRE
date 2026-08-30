from langchain_groq import ChatGroq

from app.domain.interfaces.llm_provider import LLMProvider


class GroqProvider(LLMProvider):
    """Provider responsável pela comunicação com a Groq."""

    def __init__(
        self,
        api_key: str,
        model: str = "openai/gpt-oss-20b",
        temperature: float = 0.0,
    ) -> None:
        self._client = ChatGroq(
            api_key=api_key,
            model=model,
            temperature=temperature,
        )

    def generate_response(self, prompt: str) -> str:
        try:
            response = self._client.invoke(prompt)
        except Exception as error:
            raise RuntimeError("Não foi possível obter uma resposta da Groq.") from error

        if not isinstance(response.content, str):
            raise RuntimeError("A Groq retornou uma resposta em formato inválido.")

        return response.content
