class RepositoryError(Exception):
    """Falha de infraestrutura ao acessar a persistência (ex.: MongoDB indisponível)."""


class NotFoundError(Exception):
    """Recurso solicitado não existe. A mensagem é exibida ao cliente da API."""


class ConflictError(Exception):
    """Operação viola uma regra de unicidade (ex.: e-mail já cadastrado). A mensagem é exibida ao cliente."""


class LLMProviderError(Exception):
    """Falha ao obter uma resposta válida do provedor de LLM."""
