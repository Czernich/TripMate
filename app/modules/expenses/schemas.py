from decimal import Decimal
from typing import Annotated

from pydantic import (
    AfterValidator,
    BaseModel,
    Field,
    StringConstraints,
)

SUPPORTED_CURRENCIES = {"PLN", "EUR", "USD"}


def normalize_currency(value: str) -> str:
    currency = value.strip().upper()

    if currency not in SUPPORTED_CURRENCIES:
        raise ValueError("Unsupported currency")

    return currency


ExpenseDescription = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        min_length=1,
        max_length=500,
    ),
]

ExpenseAmount = Annotated[
    Decimal,
    Field(
        gt=0,
        max_digits=12,
        decimal_places=2,
    ),
]

ExpenseCurrency = Annotated[
    str,
    AfterValidator(normalize_currency),
]


class ExpenseCreate(BaseModel):
    trip_id: int = Field(gt=0)
    payer_user_id: int = Field(gt=0)
    description: ExpenseDescription
    amount: ExpenseAmount
    currency: ExpenseCurrency
