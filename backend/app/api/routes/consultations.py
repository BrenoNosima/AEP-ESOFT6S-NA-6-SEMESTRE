from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from pymongo.database import Database

from app.core.config import settings
from app.database.mongodb import get_database
from app.domain.exceptions import RepositoryError
from app.domain.interfaces.consultation_repository import ConsultationRepository
from app.domain.interfaces.llm_provider import LLMProvider
from app.domain.models.consultation import Consultation
from app.llm.providers.groq_provider import GroqProvider
from app.repositories.mongo_consultation_repository import MongoConsultationRepository
from app.services.consultation_service import ConsultationService
from app.services.sustainability_service import SustainabilityService

router = APIRouter(prefix="/consultations", tags=["consultations"])


class ConsultationRequest(BaseModel):
    question: str
    category: str


class ConsultationResponse(BaseModel):
    id: str
    question: str
    category: str
    answer: str
    created_at: datetime

    @classmethod
    def from_domain(cls, consultation: Consultation) -> "ConsultationResponse":
        return cls(
            id=consultation.id,
            question=consultation.question,
            category=consultation.category,
            answer=consultation.answer,
            created_at=consultation.created_at,
        )


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


_DATA_UNAVAILABLE = "Serviço de dados indisponível. Tente novamente."


@router.post("", response_model=ConsultationResponse, status_code=201)
def create_consultation(
    request: ConsultationRequest,
    service: ConsultationService = Depends(get_consultation_service),
) -> ConsultationResponse:
    try:
        consultation = service.create_consultation(request.question, request.category)
    except RepositoryError as error:
        raise HTTPException(status_code=503, detail=_DATA_UNAVAILABLE) from error
    except RuntimeError as error:
        raise HTTPException(status_code=502, detail=str(error)) from error
    return ConsultationResponse.from_domain(consultation)


@router.get("", response_model=list[ConsultationResponse])
def list_consultations(
    service: ConsultationService = Depends(get_consultation_service),
) -> list[ConsultationResponse]:
    try:
        consultations = service.list_consultations()
    except RepositoryError as error:
        raise HTTPException(status_code=503, detail=_DATA_UNAVAILABLE) from error
    return [ConsultationResponse.from_domain(c) for c in consultations]


@router.get("/{consultation_id}", response_model=ConsultationResponse)
def get_consultation(
    consultation_id: str,
    service: ConsultationService = Depends(get_consultation_service),
) -> ConsultationResponse:
    try:
        consultation = service.get_consultation(consultation_id)
    except RepositoryError as error:
        raise HTTPException(status_code=503, detail=_DATA_UNAVAILABLE) from error
    if consultation is None:
        raise HTTPException(status_code=404, detail="Consulta não encontrada.")
    return ConsultationResponse.from_domain(consultation)


@router.delete("/{consultation_id}", status_code=204)
def delete_consultation(
    consultation_id: str,
    service: ConsultationService = Depends(get_consultation_service),
) -> None:
    try:
        deleted = service.delete_consultation(consultation_id)
    except RepositoryError as error:
        raise HTTPException(status_code=503, detail=_DATA_UNAVAILABLE) from error
    if not deleted:
        raise HTTPException(status_code=404, detail="Consulta não encontrada.")
