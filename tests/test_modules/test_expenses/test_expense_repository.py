from decimal import Decimal

import pytest

from app.models import TripParticipant
from app.models.expense import Expense
from app.models.trip import Trip
from app.models.user import User
from app.modules.expenses.repository import ExpenseRepository


@pytest.mark.asyncio
async def test_add_expense(
    expense_repository: ExpenseRepository,
    saved_expense: Expense,
):
    result = await expense_repository.add(saved_expense)

    assert result.id is not None
    assert result.amount == Decimal("250.00")
    assert result.currency == "PLN"


@pytest.mark.asyncio
async def test_get_trip_by_id(
    expense_repository: ExpenseRepository,
    saved_trip: Trip,
):
    result = await expense_repository.get_trip_by_id(saved_trip.id)

    assert result is not None
    assert result.id == saved_trip.id


@pytest.mark.asyncio
async def test_get_trip_by_id_returns_none_for_missing_trip(
    expense_repository: ExpenseRepository,
):
    result = await expense_repository.get_trip_by_id(999999)

    assert result is None


@pytest.mark.asyncio
async def test_get_trip_by_id_returns_none_for_deleted_trip(
    expense_repository: ExpenseRepository,
    deleted_trip: Trip,
):
    result = await expense_repository.get_trip_by_id(deleted_trip.id)

    assert result is None


@pytest.mark.asyncio
async def test_get_active_user_by_id(
    expense_repository: ExpenseRepository,
    saved_user: User,
):
    result = await expense_repository.get_active_user_by_id(saved_user.id)

    assert result is not None
    assert result.id == saved_user.id


@pytest.mark.asyncio
async def test_get_active_user_by_id_returns_none_for_inactive_user(
    expense_repository: ExpenseRepository,
    inactive_user: User,
):
    result = await expense_repository.get_active_user_by_id(inactive_user.id)

    assert result is None


@pytest.mark.asyncio
async def test_get_active_user_by_id_returns_none_for_missing_user(
    expense_repository: ExpenseRepository,
):
    result = await expense_repository.get_active_user_by_id(999999)

    assert result is None


@pytest.mark.asyncio
async def test_is_trip_participant_returns_true(
    expense_repository: ExpenseRepository,
    saved_participant: TripParticipant,
):
    result = await expense_repository.is_trip_participant(
        trip_id=saved_participant.trip_id,
        user_id=saved_participant.user_id,
    )

    assert result is True


@pytest.mark.asyncio
async def test_is_trip_participant_returns_false(
    expense_repository: ExpenseRepository,
    saved_participant: TripParticipant,
):
    result = await expense_repository.is_trip_participant(
        trip_id=saved_participant.trip_id + 1,
        user_id=saved_participant.user_id,
    )

    assert result is False
