from app.domain.exceptions import LLMProviderError
from app.domain.interfaces.llm_provider import LLMProvider
from app.domain.models.category import Category


class SustainabilityService:
    """Gera orientações sustentáveis com o provedor de LLM recebido."""

    def __init__(self, llm_provider: LLMProvider) -> None:
        self._llm_provider = llm_provider

    def classify_category(self, user_question: str) -> Category:
        """Classifica uma pergunta usando somente as categorias do domínio."""
        allowed_categories = ", ".join(category.value for category in Category)
        prompt = (
            "Classifique a pergunta de sustentabilidade abaixo em exatamente uma "
            "das categorias permitidas. Responda somente com o nome da categoria, "
            "sem explicações, pontuação ou texto adicional.\n\n"
            f"Categorias permitidas: {allowed_categories}.\n\n"
            f"Pergunta do usuário: {user_question}"
        )

        response = self._llm_provider.generate_response(prompt)
        if not isinstance(response, str):
            raise LLMProviderError("A LLM retornou uma categoria em formato inválido.")

        normalized_category = response.strip().lower()
        try:
            return Category(normalized_category)
        except ValueError as error:
            raise LLMProviderError("A LLM retornou uma categoria inválida.") from error

    def generate_guidance(
        self,
        user_question: str,
        *,
        city: str | None = None,
        state: str | None = None,
    ) -> str:
        if city and state:
            location_context = f"Cidade do usuário: {city}. Estado: {state}."
        else:
            location_context = "A localização do usuário não foi informada."

        prompt = (
            "Responda à pergunta abaixo em português, de maneira simples e "
            "objetiva. Foque em sustentabilidade e forneça orientações práticas, "
            "evitando uma resposta excessivamente longa. Use a localização somente "
            "quando ela for relevante para a orientação. Não invente endereços, "
            "pontos de coleta, horários de atendimento ou regras municipais. Se "
            "não houver informação confiável e específica para o município, "
            "reconheça essa limitação e recomende os canais oficiais da prefeitura.\n\n"
            f"{location_context}\n\n"
            f"Pergunta do usuário: {user_question}"
        )

        return self._llm_provider.generate_response(prompt)
