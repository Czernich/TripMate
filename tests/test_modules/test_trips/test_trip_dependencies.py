from unittest.mock import Mock

from app.modules.trips.dependencies import (
    get_trip_repository,
    get_trip_service,
)


def test_get_trip_repository_creates_repository_with_provided_session():
    fake_db_session = Mock()

    repository = get_trip_repository(fake_db_session)

    assert repository.session is fake_db_session


def test_get_trip_service_creates_service_with_provided_repository():
    fake_repository = Mock()

    service = get_trip_service(fake_repository)

    assert service.repository is fake_repository
