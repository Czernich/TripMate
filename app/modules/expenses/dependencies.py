from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.modules.expenses.repository import ExpenseRepository
from app.modules.expenses.service import ExpenseService

SessionDep = Annotated[
    AsyncSession,
    Depends(get_db, scope="function"),
]


def get_expense_repository(
    session: SessionDep,
) -> ExpenseRepository:
    return ExpenseRepository(session)


ExpenseRepositoryDep = Annotated[
    ExpenseRepository,
    Depends(get_expense_repository),
]


def get_expense_service(
    repository: ExpenseRepositoryDep,
) -> ExpenseService:
    return ExpenseService(
        repository=repository,
    )


ExpenseServiceDep = Annotated[
    ExpenseService,
    Depends(get_expense_service),
]
