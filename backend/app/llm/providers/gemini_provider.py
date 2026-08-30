from langchain_google_genai import ChatGoogleGenerativeAI

from app.domain.interfaces.llm_provider import LLMProvider


class GeminiProvider(LLMProvider):
    """Provider responsável pela comunicação com o Gemini."""

    def __init__(
        self,
        api_key: str,
        model: str,
        temperature: float = 0.0,
    ) -> None:
        self._client = ChatGoogleGenerativeAI(
            google_api_key=api_key,
            model=model,
            temperature=temperature,
        )

    def generate_response(self, prompt: str) -> str:
        try:
            response = self._client.invoke(prompt)
        except Exception as error:
            raise RuntimeError("Não foi possível obter uma resposta do Gemini.") from error

        if not isinstance(response.content, str):
            raise RuntimeError("O Gemini retornou uma resposta em formato inválido.")

        return response.content
