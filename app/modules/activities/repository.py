from sqlalchemy.ext.asyncio import AsyncSession

from app.models.activity import Activity


class ActivityRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(self, activity: Activity) -> Activity:
        self.session.add(activity)

        await self.session.flush()
        await self.session.refresh(activity)
        return activity
