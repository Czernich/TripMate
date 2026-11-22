from decimal import Decimal

import pytest
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.expense import Expense
from app.models.trip import Trip
from app.models.trip_participant import TripParticipant
from app.models.user import User
from app.modules.expenses.exceptions import (
    ExpensePayerNotFoundException,
    ExpensePayerNotParticipantException,
    ExpenseTripNotFoundException,
)
from app.modules.expenses.schemas import ExpenseCreate
from app.modules.expenses.service import ExpenseService


def create_expense_payload(**overrides):
    payload = {
        "trip_id": 1,
        "payer_user_id": 1,
        "description": "Hotel accommodation",
        "amount": Decimal("250.00"),
        "currency": "PLN",
    }
    payload.update(overrides)

    return ExpenseCreate(**payload)


async def assert_no_expenses(db_session: AsyncSession):
    result = await db_session.scalar(select(func.count()).select_from(Expense))

    assert result == 0


@pytest.mark.asyncio
async def test_create_expense(
    expense_service: ExpenseService,
    saved_trip: Trip,
    saved_user: User,
    saved_participant: TripParticipant,
):
    payload = create_expense_payload(
        trip_id=saved_trip.id,
        payer_user_id=saved_user.id,
    )

    expense = await expense_service.create_expense(payload)

    assert expense.id is not None
    assert expense.trip_id == saved_trip.id
    assert expense.payer_user_id == saved_user.id
    assert expense.description == "Hotel accommodation"
    assert expense.amount == Decimal("250.00")
    assert expense.currency == "PLN"


@pytest.mark.asyncio
async def test_create_expense_trip_not_found(
    expense_service: ExpenseService,
    db_session: AsyncSession,
    saved_user: User,
):
    payload = create_expense_payload(
        payer_user_id=saved_user.id,
    )

    with pytest.raises(ExpenseTripNotFoundException):
        await expense_service.create_expense(payload)

    await assert_no_expenses(db_session)


@pytest.mark.asyncio
async def test_create_expense_trip_deleted(
    expense_service: ExpenseService,
    deleted_trip: Trip,
    saved_user: User,
    db_session: AsyncSession,
):
    payload = create_expense_payload(
        trip_id=deleted_trip.id,
        payer_user_id=saved_user.id,
    )

    with pytest.raises(ExpenseTripNotFoundException):
        await expense_service.create_expense(payload)

    await assert_no_expenses(db_session)


@pytest.mark.asyncio
async def test_create_expense_payer_not_found(
    expense_service: ExpenseService,
    saved_trip: Trip,
    db_session: AsyncSession,
):
    payload = create_expense_payload(
        trip_id=saved_trip.id,
    )

    with pytest.raises(ExpensePayerNotFoundException):
        await expense_service.create_expense(payload)

    await assert_no_expenses(db_session)


@pytest.mark.asyncio
async def test_create_expense_payer_inactive(
    expense_service: ExpenseService,
    saved_trip: Trip,
    inactive_user: User,
    db_session: AsyncSession,
):
    payload = create_expense_payload(
        trip_id=saved_trip.id,
        payer_user_id=inactive_user.id,
    )

    with pytest.raises(ExpensePayerNotFoundException):
        await expense_service.create_expense(payload)

    await assert_no_expenses(db_session)


@pytest.mark.asyncio
async def test_create_expense_payer_not_participant(
    expense_service: ExpenseService,
    saved_trip: Trip,
    saved_user: User,
    db_session: AsyncSession,
):
    payload = create_expense_payload(
        trip_id=saved_trip.id,
        payer_user_id=saved_user.id,
    )

    with pytest.raises(ExpensePayerNotParticipantException):
        await expense_service.create_expense(payload)

    await assert_no_expenses(db_session)


@pytest.mark.asyncio
async def test_create_expense_rollback(
    expense_service: ExpenseService,
    saved_trip: Trip,
    saved_user: User,
    saved_participant: TripParticipant,
    db_session: AsyncSession,
):
    payload = create_expense_payload(
        trip_id=saved_trip.id,
        payer_user_id=saved_user.id,
    )

    expense = await expense_service.create_expense(payload)

    assert expense.id is not None

    await db_session.rollback()

    await assert_no_expenses(db_session)
