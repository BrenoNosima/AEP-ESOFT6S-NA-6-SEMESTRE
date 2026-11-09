class RepositoryError(Exception):
    """Falha de infraestrutura ao acessar a persistência (ex.: MongoDB indisponível)."""


class NotFoundError(Exception):
    """Recurso solicitado não existe. A mensagem é exibida ao cliente da API."""


class LLMProviderError(Exception):
    """Falha ao obter uma resposta válida do provedor de LLM."""
