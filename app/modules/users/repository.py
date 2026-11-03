from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.modules.users.exceptions import UserAlreadyExistsException


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(self, user: User) -> User:
        self.session.add(user)

        try:
            await self.session.flush()
            await self.session.refresh(user)

        except IntegrityError as exc:
            original_exception = exc.orig.__cause__
            constraint_name = getattr(
                original_exception,
                "constraint_name",
                None,
            )

            await self.session.rollback()

            if constraint_name == "users_email_key":
                raise UserAlreadyExistsException() from exc

            raise

        return user

    async def get_by_id(self, user_id: int) -> User | None:
        result = await self.session.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> User | None:
        result = await self.session.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()
