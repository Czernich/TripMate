from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
import os
from typing import Generator

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./tripmate.db")
POOL_SIZE = int(os.getenv("DB_POOL_SIZE", "10"))
MAX_OVERFLOW = int(os.getenv("DB_MAX_OVERFLOW", "5"))
POOL_TIMEOUT = int(os.getenv("DB_POOL_TIMEOUT", "30"))
POOL_RECYCLE = int(os.getenv("DB_POOL_RECYCLE", "1800"))
ECHO = os.getenv("DB_ECHO", "false").lower() == "true"


"""
Connection pooling settings (documented):
    - pool_size (env DB_POOL_SIZE, default 10):
        Number of connections kept permanently open in the pool for
        the lifetime of the app process.
    - max_overflow (env DB_MAX_OVERFLOW, default 5):
        Extra connections allowed above pool_size
    - pool_timeout (env DB_POOL_TIMEOUT, default 30s):
        How long a request waits for a free connection before
        SQLAlchemy raises a TimeoutError, instead of hanging forever.
    - pool_recycle (env DB_POOL_RECYCLE, default 1800s / 30 min):
        Connections older than this are closed and re-opened, even if
        still healthy.
"""

engine = create_engine(
    DATABASE_URL,
    pool_size=POOL_SIZE,
    max_overflow=MAX_OVERFLOW,
    pool_timeout=POOL_TIMEOUT,
    pool_recycle=POOL_RECYCLE,
    echo=ECHO,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
)

SessionLocal = sessionmaker(bind=engine)


def get_db() -> Generator[Session, None, None]:
    with SessionLocal() as session:
        try:
            yield session
        except Exception:
            session.rollback()
            raise