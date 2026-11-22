from app.models.expense import Expense
from app.modules.expenses.exceptions import (
    ExpensePayerNotFoundException,
    ExpensePayerNotParticipantException,
    ExpenseTripNotFoundException,
)
from app.modules.expenses.repository import ExpenseRepository
from app.modules.expenses.schemas import ExpenseCreate


class ExpenseService:
    def __init__(self, repository: ExpenseRepository):
        self.repository = repository

    async def create_expense(self, payload: ExpenseCreate) -> Expense:
        trip = await self.repository.get_trip_by_id(payload.trip_id)

        if not trip:
            raise ExpenseTripNotFoundException()

        payer = await self.repository.get_active_user_by_id(payload.payer_user_id)

        if not payer:
            raise ExpensePayerNotFoundException()

        is_participant = await self.repository.is_trip_participant(
            trip_id=payload.trip_id,
            user_id=payload.payer_user_id,
        )

        if not is_participant:
            raise ExpensePayerNotParticipantException()

        expense = Expense(
            trip_id=payload.trip_id,
            payer_user_id=payload.payer_user_id,
            description=payload.description,
            amount=payload.amount,
            currency=payload.currency,
        )

        return await self.repository.add(expense)
