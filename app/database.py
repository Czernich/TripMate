from collections.abc import AsyncGenerator

from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.exceptions import DatabaseUnavailableException
from app.settings import settings_db


class Base(DeclarativeBase):
    pass


engine = create_async_engine(settings_db.async_database_url)

SessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        try:
            yield session
            await session.commit()
        except (OperationalError, OSError) as exc:
            await session.rollback()
            raise DatabaseUnavailableException() from exc
        except Exception:
            await session.rollback()
            raise
