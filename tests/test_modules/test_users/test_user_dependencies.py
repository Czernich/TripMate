from unittest.mock import MagicMock

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.users.dependencies import (
    get_user_repository,
    get_user_service,
)
from app.modules.users.repository import UserRepository
from app.modules.users.service import UserService


def test_get_user_repository_creates_repository_with_provided_session():
    session = MagicMock(spec=AsyncSession)

    repository = get_user_repository(session)

    assert isinstance(repository, UserRepository)
    assert repository.session is session


def test_get_user_service_creates_service_with_provided_repository():
    repository = MagicMock(spec=UserRepository)

    service = get_user_service(repository)

    assert isinstance(service, UserService)
    assert service.repository is repository
