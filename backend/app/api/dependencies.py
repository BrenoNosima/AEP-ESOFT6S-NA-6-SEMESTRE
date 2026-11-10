"""Composition root: único lugar que conhece as implementações concretas.

Rotas e services dependem apenas das interfaces do domínio; aqui elas são
ligadas às implementações reais (Groq, MongoDB) via `Depends`.
"""

from __future__ import annotations

from functools import lru_cache

from fastapi import Depends
from pymongo.database import Database

from app.api.repositories.mongo_consultation_repository import MongoConsultationRepository
from app.api.repositories.mongo_user_repository import MongoUserRepository
from app.api.services.consultation_service import ConsultationService
from app.api.services.sustainability_service import SustainabilityService
from app.api.services.user_service import UserService
from app.core.config import settings
from app.database.mongodb import get_database
from app.domain.interfaces.consultation_repository import ConsultationRepository
from app.domain.interfaces.llm_provider import LLMProvider
from app.domain.interfaces.user_repository import UserRepository
from app.llm.providers.groq_provider import GroqProvider


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


def get_user_repository(
    database: Database = Depends(get_database),
) -> UserRepository:
    return MongoUserRepository(database)


def get_user_service(
    users: UserRepository = Depends(get_user_repository),
    consultations: ConsultationRepository = Depends(get_consultation_repository),
) -> UserService:
    return UserService(users, consultations)
