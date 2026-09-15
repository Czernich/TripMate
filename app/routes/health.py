import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/health", status_code=200)
async def health_check():
    return {"status": "ok"}


@router.get("/health/db", status_code=200)
async def health_db_check(db: AsyncSession = Depends(get_db)):  # noqa: B008
    try:
        await db.execute(text("SELECT 1"))
    except Exception:
        logger.exception("Database health check failed")
        raise HTTPException(status_code=503, detail="Database unavailable")
    return {"status": "ok"}
