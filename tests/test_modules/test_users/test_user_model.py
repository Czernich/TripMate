import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from tests.factories import UserFactory


@pytest.mark.asyncio
async def test_create_user_with_valid_data(db_session: AsyncSession):
    user = UserFactory.build()
    db_session.add(user)
    await db_session.flush()
    await db_session.refresh(user)

    assert user.id is not None
    assert user.created_at is not None
    assert user.updated_at is not None
    assert user.is_active is True
    assert user.email == "user1@tripmate.com"
    assert user.password_hash == "$2a$12$qNvf9ovKdIaAQu9rSUZvKOlE"
    assert user.display_name == "TripMate"


@pytest.mark.asyncio
async def test_creating_users_with_duplicate_emails_raises_integrity_error(
    db_session: AsyncSession,
):
    user1 = UserFactory.build()
    user2 = UserFactory.build()
    db_session.add_all([user1, user2])

    with pytest.raises(IntegrityError):
        await db_session.flush()
