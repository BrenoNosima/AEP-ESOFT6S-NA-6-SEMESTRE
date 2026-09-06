from fastapi import FastAPI

from app.api.router import router as consultations_router
from app.api.routes import health
from app.core.config import settings

app = FastAPI(title=settings.app_name)

app.include_router(health.router)
app.include_router(consultations_router)
