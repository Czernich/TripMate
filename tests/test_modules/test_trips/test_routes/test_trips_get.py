import pytest


async def test_get_trip_returns_200_with_persisted_fields(client, saved_trip):
    trip = saved_trip
    response = await client.get(f"/trips/{trip.id}")

    assert response.status_code == 200
    assert response.json() == {
        "id": trip.id,
        "name": trip.name,
        "destination": trip.destination,
        "start_date": str(trip.start_date),
        "end_date": str(trip.end_date),
    }


async def test_get_trip_returns_404_when_missing(client):
    response = await client.get("/trips/999999")

    assert response.status_code == 404
    assert response.json() == {
        "error": {
            "code": "TRIP_NOT_FOUND",
            "message": "Trip with id 999999 was not found.",
        }
    }


@pytest.mark.parametrize("trip_id", ["abc", "1.5", "0", "-5"])
async def test_get_trip_returns_422_for_invalid_id(client, trip_id):
    response = await client.get(f"/trips/{trip_id}")

    assert response.status_code == 422


async def test_get_trip_returns_503_when_database_unavailable(
    client, database_unavailable
):
    response = await client.get("/trips/1")

    assert response.status_code == 503
    assert response.json() == {
        "error": {
            "code": "SERVICE_UNAVAILABLE",
            "message": "Database is currently unavailable. Please try again later.",
        }
    }
