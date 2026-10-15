from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.api.deps import db_session
from app.core.config import settings

router = APIRouter(tags=["health"])


@router.get("/health")
def health(db: Session = Depends(db_session)):
    db_status = "ok"
    try:
        db.execute(text("SELECT 1"))
    except Exception as e:  # noqa: BLE001
        db_status = f"error: {e!s}"

    return {
        "app": settings.app_name,
        "env": settings.env,
        "db": db_status,
    }
