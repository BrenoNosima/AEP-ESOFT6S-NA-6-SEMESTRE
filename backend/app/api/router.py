from __future__ import annotations

from functools import lru_cache

from fastapi import APIRouter, Depends, HTTPException, Query
from pymongo.database import Database

from app.api.repositories.mongo_consultation_repository import MongoConsultationRepository
from app.api.schemas import (
    ConsultationCategory,
    ConsultationCategoryUpdate,
    ConsultationRequest,
    ConsultationResponse,
)
from app.api.services.consultation_service import ConsultationService
from app.api.services.sustainability_service import SustainabilityService
from app.core.config import settings
from app.database.mongodb import get_database
from app.domain.exceptions import RepositoryError
from app.domain.interfaces.consultation_repository import ConsultationRepository
from app.domain.interfaces.llm_provider import LLMProvider
from app.llm.providers.groq_provider import GroqProvider

router = APIRouter(prefix="/consultations", tags=["consultations"])

_NOT_FOUND = "Consulta não encontrada."
_DATA_UNAVAILABLE = "Serviço de dados indisponível. Tente novamente."

_ERRORS = {
    404: {"description": "Consulta não encontrada."},
    502: {"description": "A LLM (Groq) não respondeu ou retornou algo inválido."},
    503: {"description": "MongoDB indisponível."},
}


@lru_cache
def get_llm_provider() -> LLMProvider:
    return GroqProvider(api_key=settings.groq_api_key, model=settings.groq_model)


def get_sustainability_service(
    llm_provider: LLMProvider = Depends(get_llm_provider),
) -> SustainabilityService:
    return SustainabilityService(llm_provider)


def get_consultation_repository(
    database: Database = Depends(get_database),
) -> ConsultationRepository:
    return MongoConsultationRepository(database)


def get_consultation_service(
    sustainability_service: SustainabilityService = Depends(get_sustainability_service),
    repository: ConsultationRepository = Depends(get_consultation_repository),
) -> ConsultationService:
    return ConsultationService(sustainability_service, repository)


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
    try:
        consultation = service.create_consultation(
            request.question, request.category.value
        )
    except RepositoryError as error:
        raise HTTPException(status_code=503, detail=_DATA_UNAVAILABLE) from error
    except RuntimeError as error:
        raise HTTPException(status_code=502, detail=str(error)) from error
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
    try:
        consultations = service.list_consultations(
            category=category.value if category else None, limit=limit, skip=skip
        )
    except RepositoryError as error:
        raise HTTPException(status_code=503, detail=_DATA_UNAVAILABLE) from error
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
    try:
        consultation = service.get_consultation(consultation_id)
    except RepositoryError as error:
        raise HTTPException(status_code=503, detail=_DATA_UNAVAILABLE) from error
    if consultation is None:
        raise HTTPException(status_code=404, detail=_NOT_FOUND)
    return ConsultationResponse.from_domain(consultation)


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
    try:
        consultation = service.update_consultation_category(
            consultation_id, request.category.value
        )
    except RepositoryError as error:
        raise HTTPException(status_code=503, detail=_DATA_UNAVAILABLE) from error
    if consultation is None:
        raise HTTPException(status_code=404, detail=_NOT_FOUND)
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
    try:
        deleted = service.delete_consultation(consultation_id)
    except RepositoryError as error:
        raise HTTPException(status_code=503, detail=_DATA_UNAVAILABLE) from error
    if not deleted:
        raise HTTPException(status_code=404, detail=_NOT_FOUND)
