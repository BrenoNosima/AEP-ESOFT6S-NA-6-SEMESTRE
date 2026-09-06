from app.domain.interfaces.llm_provider import LLMProvider


class SustainabilityService:
    """Gera orientações sustentáveis com o provedor de LLM recebido."""

    def __init__(self, llm_provider: LLMProvider) -> None:
        self._llm_provider = llm_provider

    def generate_guidance(self, user_question: str) -> str:
        prompt = (
            "Responda à pergunta abaixo em português, de maneira simples e "
            "objetiva. Foque em sustentabilidade e forneça orientações práticas, "
            "evitando uma resposta excessivamente longa. Não invente locais "
            "específicos de coleta. Quando a orientação depender de regras da "
            "cidade ou região do usuário, informe essa dependência.\n\n"
            f"Pergunta do usuário: {user_question}"
        )

        return self._llm_provider.generate_response(prompt)
