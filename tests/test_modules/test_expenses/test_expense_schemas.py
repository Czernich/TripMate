from decimal import Decimal

import pytest
from pydantic import ValidationError

from app.modules.expenses.schemas import ExpenseCreate


def valid_payload(**overrides):
    payload = {
        "trip_id": 1,
        "payer_user_id": 1,
        "description": "Hotel accommodation",
        "amount": Decimal("250.00"),
        "currency": "PLN",
    }
    payload.update(overrides)
    return payload


def test_expense_create_valid_payload():
    expense = ExpenseCreate(**valid_payload())

    assert expense.trip_id == 1
    assert expense.payer_user_id == 1
    assert expense.description == "Hotel accommodation"
    assert expense.amount == Decimal("250.00")
    assert expense.currency == "PLN"


def test_expense_create_strips_description_whitespace():
    expense = ExpenseCreate(**valid_payload(description="  Hotel accommodation  "))

    assert expense.description == "Hotel accommodation"


@pytest.mark.parametrize(
    "description",
    ["", " ", "   "],
)
def test_expense_create_rejects_blank_description(description):
    with pytest.raises(ValidationError):
        ExpenseCreate(**valid_payload(description=description))


def test_expense_create_rejects_description_over_500_characters():
    with pytest.raises(ValidationError):
        ExpenseCreate(**valid_payload(description="a" * 501))


@pytest.mark.parametrize(
    "amount",
    [
        Decimal(0),
        Decimal(-1),
        Decimal("-0.01"),
    ],
)
def test_expense_create_rejects_non_positive_amount(amount):
    with pytest.raises(ValidationError):
        ExpenseCreate(**valid_payload(amount=amount))


def test_expense_create_accepts_maximum_amount():
    expense = ExpenseCreate(**valid_payload(amount=Decimal("9999999999.99")))

    assert expense.amount == Decimal("9999999999.99")


@pytest.mark.parametrize(
    "amount",
    [
        Decimal("1.001"),
        Decimal("1.234"),
    ],
)
def test_expense_create_rejects_excessive_amount_precision(amount):
    with pytest.raises(ValidationError):
        ExpenseCreate(**valid_payload(amount=amount))


@pytest.mark.parametrize(
    "currency, expected",
    [
        ("pln", "PLN"),
        (" eur ", "EUR"),
        (" UsD ", "USD"),
    ],
)
def test_expense_create_normalizes_currency(currency, expected):
    expense = ExpenseCreate(**valid_payload(currency=currency))

    assert expense.currency == expected


@pytest.mark.parametrize(
    "currency",
    [
        "",
        "GBP",
        "PL",
        "PLNN",
        "123",
    ],
)
def test_expense_create_rejects_unsupported_currency(currency):
    with pytest.raises(ValidationError):
        ExpenseCreate(**valid_payload(currency=currency))


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("trip_id", 0),
        ("payer_user_id", -1),
    ],
)
def test_expense_create_rejects_non_positive_ids(field, value):
    with pytest.raises(ValidationError):
        ExpenseCreate(**valid_payload(**{field: value}))
