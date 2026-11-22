from decimal import Decimal

import pytest
from sqlalchemy.exc import DBAPIError, IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.expense import Expense


@pytest.mark.parametrize(
    "amount",
    [
        Decimal("0.00"),
        Decimal("-10.00"),
    ],
)
async def test_expense_requires_positive_amount(
    db_session: AsyncSession,
    saved_expense: Expense,
    amount: Decimal,
):
    saved_expense.amount = amount

    with pytest.raises(IntegrityError):
        await db_session.flush()


@pytest.mark.parametrize(
    "description",
    [
        "",
        " ",
        "   ",
    ],
)
async def test_expense_requires_non_empty_description(
    db_session: AsyncSession,
    saved_expense: Expense,
    description: str,
):
    saved_expense.description = description

    with pytest.raises(IntegrityError):
        await db_session.flush()


@pytest.mark.parametrize(
    "currency",
    [
        "",
        "EU",
        "eur",
    ],
)
async def test_expense_requires_valid_currency(
    db_session: AsyncSession,
    saved_expense: Expense,
    currency: str,
):
    saved_expense.currency = currency

    with pytest.raises(IntegrityError):
        await db_session.flush()


async def test_expense_rejects_currency_longer_than_three_characters(
    db_session: AsyncSession,
    saved_expense: Expense,
):
    saved_expense.currency = "EURO"

    with pytest.raises(DBAPIError):
        await db_session.flush()
