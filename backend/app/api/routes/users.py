from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from app.api.dependencies import get_user_service
from app.api.schemas import (
    AddressSchema,
    ConsultationResponse,
    UserConsultationsSummary,
    UserCreate,
    UserResponse,
)
from app.api.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["users"])

# Só documentação do OpenAPI: a tradução erro -> status fica nos
# exception_handlers do main.py.
_ERRORS = {
    404: {"description": "Usuário não encontrado."},
    409: {"description": "E-mail já cadastrado."},
    503: {"description": "MongoDB indisponível."},
}

_Limit = Query(50, ge=1, le=100, description="Máximo de itens retornados.")
_Skip = Query(0, ge=0, description="Itens a pular (paginação).")


@router.post(
    "",
    response_model=UserResponse,
    status_code=201,
    summary="Criar usuário",
    description="Cadastra um usuário com zero ou mais endereços (subdocumentos). O e-mail é único.",
    responses={409: _ERRORS[409], 503: _ERRORS[503]},
)
def create_user(
    request: UserCreate,
    service: UserService = Depends(get_user_service),
) -> UserResponse:
    user = service.create_user(
        request.name, request.email, [a.to_domain() for a in request.addresses]
    )
    return UserResponse.from_domain(user)


@router.get(
    "",
    response_model=list[UserResponse],
    summary="Listar usuários",
    description="Lista os usuários (mais recentes primeiro), paginando com `limit`/`skip`.",
    responses={503: _ERRORS[503]},
)
def list_users(
    limit: int = _Limit,
    skip: int = _Skip,
    service: UserService = Depends(get_user_service),
) -> list[UserResponse]:
    return [UserResponse.from_domain(u) for u in service.list_users(limit=limit, skip=skip)]


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="Buscar usuário por id",
    responses={404: _ERRORS[404], 503: _ERRORS[503]},
)
def get_user(
    user_id: str,
    service: UserService = Depends(get_user_service),
) -> UserResponse:
    return UserResponse.from_domain(service.get_user(user_id))


@router.post(
    "/{user_id}/addresses",
    response_model=UserResponse,
    status_code=201,
    summary="Adicionar endereço",
    description="Acrescenta um endereço à lista `addresses` do usuário.",
    responses={404: _ERRORS[404], 503: _ERRORS[503]},
)
def add_address(
    user_id: str,
    request: AddressSchema,
    service: UserService = Depends(get_user_service),
) -> UserResponse:
    return UserResponse.from_domain(service.add_address(user_id, request.to_domain()))


@router.delete(
    "/{user_id}",
    status_code=204,
    summary="Remover usuário",
    description="Remove o usuário e, em cascata, todas as consultas dele.",
    responses={404: _ERRORS[404], 503: _ERRORS[503]},
)
def delete_user(
    user_id: str,
    service: UserService = Depends(get_user_service),
) -> None:
    service.delete_user(user_id)


@router.get(
    "/{user_id}/consultations",
    response_model=list[ConsultationResponse],
    summary="Histórico de consultas do usuário",
    description="Consultas do usuário (mais recentes primeiro), paginando com `limit`/`skip`.",
    responses={404: _ERRORS[404], 503: _ERRORS[503]},
)
def list_user_consultations(
    user_id: str,
    limit: int = _Limit,
    skip: int = _Skip,
    service: UserService = Depends(get_user_service),
) -> list[ConsultationResponse]:
    consultations = service.list_consultations(user_id, limit=limit, skip=skip)
    return [ConsultationResponse.from_domain(c) for c in consultations]


@router.get(
    "/{user_id}/consultations/summary",
    response_model=UserConsultationsSummary,
    summary="Resumo das consultas por categoria",
    description="Total de consultas do usuário agrupado por categoria (agregação `$group` no MongoDB).",
    responses={404: _ERRORS[404], 503: _ERRORS[503]},
)
def summarize_user_consultations(
    user_id: str,
    service: UserService = Depends(get_user_service),
) -> UserConsultationsSummary:
    return UserConsultationsSummary.from_counts(
        user_id, service.summarize_consultations(user_id)
    )
