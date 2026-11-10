import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.api.routes import consultations, health
from app.core.config import settings
from app.domain.exceptions import (
    ConflictError,
    LLMProviderError,
    NotFoundError,
    RepositoryError,
)

logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title=settings.app_name,
    description="API do EcoMentor — orientação de sustentabilidade (ODS 12).",
    version="0.1.0",
)

app.include_router(health.router)
app.include_router(consultations.router)


# Erros de domínio -> status HTTP. Centralizado aqui para as rotas não
# repetirem try/except.
@app.exception_handler(NotFoundError)
def handle_not_found(_: Request, error: NotFoundError) -> JSONResponse:
    return JSONResponse(status_code=404, content={"detail": str(error)})


@app.exception_handler(ConflictError)
def handle_conflict(_: Request, error: ConflictError) -> JSONResponse:
    return JSONResponse(status_code=409, content={"detail": str(error)})


@app.exception_handler(RepositoryError)
def handle_repository_error(_: Request, __: RepositoryError) -> JSONResponse:
    return JSONResponse(
        status_code=503,
        content={"detail": "Serviço de dados indisponível. Tente novamente."},
    )


@app.exception_handler(LLMProviderError)
def handle_llm_provider_error(_: Request, error: LLMProviderError) -> JSONResponse:
    return JSONResponse(status_code=502, content={"detail": str(error)})
