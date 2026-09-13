from fastapi import APIRouter, Depends, HTTPException
from app.database import get_db
from sqlalchemy.orm import Session
from sqlalchemy import text

router = APIRouter()


@router.get("/health", status_code=200)
async def health_check():
    return {"status": "ok"}


@router.get("/health/db", status_code=200)
def health_db_check(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Database unavailable: {exc}")
    return {"status": "ok"}
