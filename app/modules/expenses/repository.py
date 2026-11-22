from sqlalchemy import exists, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.expense import Expense
from app.models.trip import Trip
from app.models.trip_participant import TripParticipant
from app.models.user import User


class ExpenseRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(self, expense: Expense) -> Expense:
        self.session.add(expense)

        await self.session.flush()
        await self.session.refresh(expense)

        return expense

    async def get_trip_by_id(self, trip_id: int) -> Trip | None:
        result = await self.session.execute(
            select(Trip).where(
                Trip.id == trip_id,
                Trip.deleted_at.is_(None),
            )
        )

        return result.scalar_one_or_none()

    async def get_active_user_by_id(self, user_id: int) -> User | None:
        result = await self.session.execute(
            select(User).where(
                User.id == user_id,
                User.is_active.is_(True),
            )
        )

        return result.scalar_one_or_none()

    async def is_trip_participant(
            self,
            trip_id: int,
            user_id: int,
    ) -> bool:
        result = await self.session.scalar(
            select(
                exists().where(
                    TripParticipant.trip_id == trip_id,
                    TripParticipant.user_id == user_id,
                )
            )
        )
        return bool(result)
