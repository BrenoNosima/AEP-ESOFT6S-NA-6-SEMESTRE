from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from app.api.dependencies import get_consultation_service
from app.api.schemas import (
    ConsultationCategory,
    ConsultationCategoryUpdate,
    ConsultationRequest,
    ConsultationResponse,
)
from app.api.services.consultation_service import ConsultationService

router = APIRouter(prefix="/consultations", tags=["consultations"])

# Só documentação do OpenAPI: a tradução erro -> status fica nos
# exception_handlers do main.py.
_ERRORS = {
    404: {"description": "Consulta não encontrada."},
    502: {"description": "A LLM (Groq) não respondeu ou retornou algo inválido."},
    503: {"description": "MongoDB indisponível."},
}


@router.post(
    "",
    response_model=ConsultationResponse,
    status_code=201,
    summary="Criar consulta",
    description="Recebe uma dúvida de sustentabilidade, gera a orientação via LLM (Groq) e persiste no MongoDB.",
    responses={502: _ERRORS[502], 503: _ERRORS[503]},
)
def create_consultation(
    request: ConsultationRequest,
    service: ConsultationService = Depends(get_consultation_service),
) -> ConsultationResponse:
    consultation = service.create_consultation(request.question, request.category.value)
    return ConsultationResponse.from_domain(consultation)


@router.get(
    "",
    response_model=list[ConsultationResponse],
    summary="Listar consultas",
    description="Lista as consultas (mais recentes primeiro). Filtra por `category` e pagina com `limit`/`skip`.",
    responses={503: _ERRORS[503]},
)
def list_consultations(
    category: ConsultationCategory | None = Query(None, description="Filtra por categoria."),
    limit: int = Query(50, ge=1, le=100, description="Máximo de itens retornados."),
    skip: int = Query(0, ge=0, description="Itens a pular (paginação)."),
    service: ConsultationService = Depends(get_consultation_service),
) -> list[ConsultationResponse]:
    consultations = service.list_consultations(
        category=category.value if category else None, limit=limit, skip=skip
    )
    return [ConsultationResponse.from_domain(c) for c in consultations]


@router.get(
    "/{consultation_id}",
    response_model=ConsultationResponse,
    summary="Buscar consulta por id",
    responses={404: _ERRORS[404], 503: _ERRORS[503]},
)
def get_consultation(
    consultation_id: str,
    service: ConsultationService = Depends(get_consultation_service),
) -> ConsultationResponse:
    return ConsultationResponse.from_domain(service.get_consultation(consultation_id))


@router.patch(
    "/{consultation_id}",
    response_model=ConsultationResponse,
    summary="Atualizar a categoria de uma consulta",
    description="Único campo editável. `question` e `answer` são fatos históricos e permanecem imutáveis.",
    responses={404: _ERRORS[404], 503: _ERRORS[503]},
)
def update_consultation_category(
    consultation_id: str,
    request: ConsultationCategoryUpdate,
    service: ConsultationService = Depends(get_consultation_service),
) -> ConsultationResponse:
    consultation = service.update_consultation_category(
        consultation_id, request.category.value
    )
    return ConsultationResponse.from_domain(consultation)


@router.delete(
    "/{consultation_id}",
    status_code=204,
    summary="Remover consulta",
    responses={404: _ERRORS[404], 503: _ERRORS[503]},
)
def delete_consultation(
    consultation_id: str,
    service: ConsultationService = Depends(get_consultation_service),
) -> None:
    service.delete_consultation(consultation_id)
