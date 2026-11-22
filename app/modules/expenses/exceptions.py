from fastapi import status

from app.exceptions.base import AppBaseException


class ExpenseException(AppBaseException):
    """Base exception for all expense-related errors."""


class ExpenseTripNotFoundException(ExpenseException):
    status_code = status.HTTP_404_NOT_FOUND
    error_code = "EXPENSE_TRIP_NOT_FOUND"
    message = "Trip not found."


class ExpensePayerNotFoundException(ExpenseException):
    status_code = status.HTTP_404_NOT_FOUND
    error_code = "EXPENSE_PAYER_NOT_FOUND"
    message = "Payer not found or inactive."


class ExpensePayerNotParticipantException(ExpenseException):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    error_code = "EXPENSE_PAYER_NOT_PARTICIPANT"
    message = "Payer is not a participant of this trip."
