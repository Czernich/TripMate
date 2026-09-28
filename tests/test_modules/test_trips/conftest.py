from collections.abc import Callable
from datetime import date

import pytest

from app.models.trip import Trip


@pytest.fixture
def trip_factory() -> Callable[..., Trip]:
    def create_trip(
        id=None,
        name="All inclusive",
        destination="Paris",
        start_date=date(2026, 10, 1),
        end_date=date(2026, 10, 10),
    ) -> Trip:
        return Trip(
            id=id,
            name=name,
            destination=destination,
            start_date=start_date,
            end_date=end_date,
        )

    return create_trip
