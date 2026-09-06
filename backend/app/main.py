import logging

from fastapi import FastAPI

from app.api.router import router as consultations_router
from app.api.routes import health
from app.core.config import settings

logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title=settings.app_name,
    description="API do EcoMentor — orientação de sustentabilidade (ODS 12).",
    version="0.1.0",
)

app.include_router(health.router)
app.include_router(consultations_router)
