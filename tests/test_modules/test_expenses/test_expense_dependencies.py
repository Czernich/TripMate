from unittest.mock import AsyncMock

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.expenses.dependencies import (
    get_expense_repository,
    get_expense_service,
)
from app.modules.expenses.repository import ExpenseRepository
from app.modules.expenses.service import ExpenseService


def test_get_expense_repository(db_session: AsyncSession):
    repository = get_expense_repository(db_session)

    assert isinstance(repository, ExpenseRepository)
    assert repository.session is db_session


def test_get_expense_service():
    repository = AsyncMock(spec=ExpenseRepository)

    service = get_expense_service(repository)

    assert isinstance(service, ExpenseService)
    assert service.repository is repository
