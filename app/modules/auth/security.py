from datetime import datetime, timedelta, timezone

import jwt

from app.settings import settings_db


def create_access_token(
    subject: str,
    expires_delta: timedelta | None = None,
) -> str:
    now = datetime.now(timezone.utc)
    expire = now + (
        expires_delta
        if expires_delta is not None
        else timedelta(minutes=settings_db.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    payload = {
        "sub": subject,
        "iat": now,
        "exp": expire,
    }
    return jwt.encode(
        payload,
        settings_db.JWT_SECRET_KEY,
        algorithm=settings_db.JWT_ALGORITHM,
    )
