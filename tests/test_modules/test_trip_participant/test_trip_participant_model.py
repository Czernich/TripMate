from datetime import datetime

import pytest
from sqlalchemy import delete, select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Trip, TripParticipant, TripRole, User
from tests.factories import TripFactory, TripParticipantFactory, UserFactory


async def create_entities(
    session: AsyncSession,
) -> tuple[Trip, User]:
    trip = TripFactory.build()
    user = UserFactory.build()

    session.add_all([trip, user])
    await session.flush()

    return trip, user


@pytest.mark.parametrize("role", list(TripRole))
async def test_each_role_persists(
    db_session: AsyncSession,
    role: TripRole,
):
    trip, user = await create_entities(db_session)

    participant = TripParticipantFactory.build(
        trip=trip,
        user=user,
        role=role,
    )

    db_session.add(participant)
    await db_session.flush()
    await db_session.refresh(participant)

    result = await db_session.scalar(
        select(TripParticipant).where(TripParticipant.id == participant.id)
    )

    assert result is not None
    assert result.id is not None
    assert result.role == role
    assert result.trip_id == trip.id
    assert result.user_id == user.id
    assert isinstance(result.joined_at, datetime)
    assert result.joined_at.tzinfo is not None


async def test_default_factory_role(
    db_session: AsyncSession,
):
    trip, user = await create_entities(db_session)

    participant = TripParticipantFactory.build(
        trip=trip,
        user=user,
    )

    db_session.add(participant)
    await db_session.flush()
    await db_session.refresh(participant)

    assert participant.role == TripRole.MEMBER


async def test_duplicate_membership_rejected(
    db_session: AsyncSession,
):
    trip, user = await create_entities(db_session)

    first = TripParticipantFactory.build(
        trip_id=trip.id,
        user_id=user.id,
        role=TripRole.OWNER,
    )

    db_session.add(first)
    await db_session.flush()

    duplicate = TripParticipantFactory.build(
        trip_id=trip.id,
        user_id=user.id,
        role=TripRole.MEMBER,
    )

    db_session.add(duplicate)

    with pytest.raises(IntegrityError):
        await db_session.flush()

    await db_session.rollback()


async def test_invalid_role_rejected(
    db_session: AsyncSession,
):
    trip, user = await create_entities(db_session)

    with pytest.raises(IntegrityError):
        await db_session.execute(
            text(
                "INSERT INTO trip_participants "
                "(trip_id, user_id, role) "
                "VALUES (:trip_id, :user_id, :role)"
            ),
            {
                "trip_id": trip.id,
                "user_id": user.id,
                "role": "SuperAdmin",
            },
        )

    await db_session.rollback()


@pytest.mark.parametrize("foreign_key", ["trip_id", "user_id"])
async def test_invalid_foreign_key_rejected(
    db_session: AsyncSession,
    foreign_key: str,
):
    trip, user = await create_entities(db_session)

    values = {
        "trip_id": trip.id,
        "user_id": user.id,
        "role": TripRole.MEMBER.value,
    }

    values[foreign_key] = -1

    with pytest.raises(IntegrityError):
        await db_session.execute(
            text(
                "INSERT INTO trip_participants "
                "(trip_id, user_id, role) "
                "VALUES (:trip_id, :user_id, :role)"
            ),
            values,
        )

    await db_session.rollback()


@pytest.mark.parametrize("column", ["trip_id", "user_id", "role"])
async def test_required_columns_reject_null(
    db_session: AsyncSession,
    column: str,
):
    trip, user = await create_entities(db_session)

    values = {
        "trip_id": trip.id,
        "user_id": user.id,
        "role": TripRole.MEMBER.value,
    }

    values[column] = None

    with pytest.raises(IntegrityError):
        await db_session.execute(
            text(
                "INSERT INTO trip_participants "
                "(trip_id, user_id, role) "
                "VALUES (:trip_id, :user_id, :role)"
            ),
            values,
        )

    await db_session.rollback()


async def test_participant_relationships(
    db_session: AsyncSession,
):
    trip, user = await create_entities(db_session)

    participant = TripParticipantFactory.build(
        trip=trip,
        user=user,
        role=TripRole.MEMBER,
    )

    db_session.add(participant)
    await db_session.flush()

    trip_id = trip.id
    user_id = user.id

    db_session.expire_all()

    loaded_trip = await db_session.scalar(
        select(Trip).options(selectinload(Trip.participants)).where(Trip.id == trip_id)
    )

    loaded_user = await db_session.scalar(
        select(User)
        .options(selectinload(User.trip_participations))
        .where(User.id == user_id)
    )

    assert loaded_trip is not None
    assert loaded_user is not None

    assert len(loaded_trip.participants) == 1
    assert loaded_trip.participants[0].user_id == user_id

    assert len(loaded_user.trip_participations) == 1
    assert loaded_user.trip_participations[0].trip_id == trip_id


@pytest.mark.parametrize("target", ["trip", "user"])
async def test_database_cascade_delete(
    db_session: AsyncSession,
    target: str,
):
    trip, user = await create_entities(db_session)

    participant = TripParticipantFactory.build(
        trip_id=trip.id,
        user_id=user.id,
        role=TripRole.ADMIN,
    )

    db_session.add(participant)
    await db_session.flush()

    participant_id = participant.id

    if target == "trip":
        await db_session.execute(delete(Trip).where(Trip.id == trip.id))
    else:
        await db_session.execute(delete(User).where(User.id == user.id))

    db_session.expire_all()

    remaining = await db_session.scalar(
        select(TripParticipant.id).where(TripParticipant.id == participant_id)
    )

    assert remaining is None


@pytest.mark.parametrize("target", ["trip", "user"])
async def test_orm_cascade_delete(
    db_session: AsyncSession,
    target: str,
):
    trip, user = await create_entities(db_session)

    participant = TripParticipantFactory.build(
        trip=trip,
        user=user,
        role=TripRole.VIEWER,
    )

    db_session.add(participant)
    await db_session.flush()

    participant_id = participant.id

    await db_session.delete(trip if target == "trip" else user)
    await db_session.flush()

    remaining = await db_session.scalar(
        select(TripParticipant.id).where(TripParticipant.id == participant_id)
    )

    assert remaining is None


async def test_soft_delete_trip_preserves_participants(
    db_session: AsyncSession,
):
    trip, user = await create_entities(db_session)

    participant = TripParticipantFactory.build(
        trip=trip,
        user=user,
    )

    db_session.add(participant)
    await db_session.flush()

    trip.deleted_at = datetime.now().astimezone()
    await db_session.flush()

    remaining = await db_session.scalar(
        select(TripParticipant.id).where(TripParticipant.id == participant.id)
    )

    assert remaining == participant.id


async def test_model_defines_expected_indexes():
    indexes = {
        index.name: tuple(column.name for column in index.columns)
        for index in TripParticipant.__table__.indexes
    }

    print([index.name for index in TripParticipant.__table__.indexes])

    assert indexes["ix_trip_participants_trip_id"] == ("trip_id",)
    assert indexes["ix_trip_participants_user_id"] == ("user_id",)
