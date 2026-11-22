import pytest

from app.modules.expenses.exceptions import (
    ExpensePayerNotFoundException,
    ExpensePayerNotParticipantException,
    ExpenseTripNotFoundException,
)


@pytest.mark.parametrize(
    "exception_class, status_code, error_code, message",
    [
        (
            ExpenseTripNotFoundException,
            404,
            "EXPENSE_TRIP_NOT_FOUND",
            "Trip not found.",
        ),
        (
            ExpensePayerNotFoundException,
            404,
            "EXPENSE_PAYER_NOT_FOUND",
            "Payer not found or inactive.",
        ),
        (
            ExpensePayerNotParticipantException,
            422,
            "EXPENSE_PAYER_NOT_PARTICIPANT",
            "Payer is not a participant of this trip.",
        ),
    ],
)
def test_expense_exception_attributes(
    exception_class,
    status_code,
    error_code,
    message,
):
    exception = exception_class()

    assert exception.status_code == status_code
    assert exception.error_code == error_code
    assert exception.message == message
