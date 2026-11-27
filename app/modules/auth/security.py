import hashlib
import hmac
from datetime import datetime, timedelta, timezone

import jwt

from app.settings import settings_db


def verify_password(plain_password: str, password_hash: str) -> bool:
    try:
        algorithm, n_str, r_str, p_str, salt_hex, hash_hex = password_hash.split("$")
        if algorithm != "scrypt":
            return False
        salt = bytes.fromhex(salt_hex)
        expected_hash = bytes.fromhex(hash_hex)
        derived_hash = hashlib.scrypt(
            plain_password.encode("utf-8"),
            salt=salt,
            n=int(n_str),
            r=int(r_str),
            p=int(p_str),
            dklen=len(expected_hash),
        )
    except (ValueError, TypeError):
        return False

    return hmac.compare_digest(derived_hash, expected_hash)


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
