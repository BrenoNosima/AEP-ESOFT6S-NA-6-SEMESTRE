from fastapi import APIRouter, Depends, HTTPException
from pymongo.database import Database
from pymongo.errors import PyMongoError

from app.database.mongodb import get_database

router = APIRouter(tags=["health"])


@router.get("/health")
def health_check(database: Database = Depends(get_database)) -> dict[str, str]:
    try:
        database.client.admin.command("ping")
    except PyMongoError as error:
        raise HTTPException(status_code=503, detail="MongoDB indisponível.") from error
    return {"status": "ok"}
