from langchain_groq import ChatGroq

from app.domain.interfaces.llm_provider import LLMProvider


class GroqProvider(LLMProvider):
    """Provider responsável pela comunicação com a Groq."""

    def __init__(
        self,
        api_key: str,
        model: str = "openai/gpt-oss-20b",
        temperature: float = 0.0,
        timeout: float = 30.0,
        max_retries: int = 2,
    ) -> None:
        try:
            self._client = ChatGroq(
                api_key=api_key,
                model=model,
                temperature=temperature,
                timeout=timeout,
                max_retries=max_retries,
            )
        except Exception as error:
            raise RuntimeError("Não foi possível inicializar o cliente da Groq.") from error

    def generate_response(self, prompt: str) -> str:
        try:
            response = self._client.invoke(prompt)
        except Exception as error:
            raise RuntimeError("Não foi possível obter uma resposta da Groq.") from error

        content = response.content

        if not isinstance(content, str):
            raise RuntimeError("A Groq retornou uma resposta em formato inválido.")

        if not content.strip():
            raise RuntimeError("A Groq retornou uma resposta vazia.")

        return content
