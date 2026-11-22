from datetime import datetime, timezone

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.trip import Trip
from app.models.trip_participant import TripParticipant, TripRole
from app.models.user import User
from app.modules.expenses.repository import ExpenseRepository
from app.modules.expenses.service import ExpenseService
from tests.factories import ExpenseFactory, TripFactory


@pytest_asyncio.fixture
async def saved_user(db_session: AsyncSession):
    user = User(
        email="john@example.com",
        display_name="John",
        password_hash="test_password_hash",
    )

    db_session.add(user)
    await db_session.flush()

    return user


@pytest_asyncio.fixture
async def inactive_user(db_session: AsyncSession, saved_user: User):
    saved_user.is_active = False

    await db_session.flush()

    return saved_user


@pytest_asyncio.fixture
async def saved_trip(db_session: AsyncSession):
    trip = TripFactory.build()

    db_session.add(trip)
    await db_session.flush()

    return trip


@pytest_asyncio.fixture
async def deleted_trip(db_session: AsyncSession):
    trip = TripFactory.build(
        deleted_at=datetime.now(timezone.utc),
    )

    db_session.add(trip)
    await db_session.flush()

    return trip


@pytest_asyncio.fixture
async def saved_participant(
    db_session: AsyncSession,
    saved_trip: Trip,
    saved_user: User,
):
    participant = TripParticipant(
        trip_id=saved_trip.id,
        user_id=saved_user.id,
        role=TripRole.MEMBER,
    )

    db_session.add(participant)
    await db_session.flush()

    return participant


@pytest_asyncio.fixture
async def saved_expense(
    db_session: AsyncSession,
    saved_trip: Trip,
    saved_user: User,
    saved_participant: TripParticipant,
):
    expense = ExpenseFactory.build(
        trip_id=saved_trip.id,
        payer_user_id=saved_user.id,
    )

    db_session.add(expense)
    await db_session.flush()

    return expense


@pytest.fixture
def expense_repository(db_session: AsyncSession):
    return ExpenseRepository(db_session)


@pytest.fixture
def expense_service(db_session: AsyncSession):
    repository = ExpenseRepository(db_session)
    return ExpenseService(repository)
