from __future__ import annotations

from functools import wraps

from pymongo.errors import PyMongoError

from app.domain.exceptions import RepositoryError


def translate_errors(method):
    """Converte qualquer PyMongoError em RepositoryError (erro de domínio).

    Compartilhado por todos os repositórios Mongo, para que nenhuma camada acima
    precise conhecer exceções do pymongo.
    """

    @wraps(method)
    def wrapper(*args, **kwargs):
        try:
            return method(*args, **kwargs)
        except PyMongoError as error:
            raise RepositoryError("Falha ao acessar o MongoDB.") from error

    return wrapper
