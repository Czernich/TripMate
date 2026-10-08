import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.asyncio
async def test_create_user_with_valid_data(db_session: AsyncSession, user_factory):
    user = user_factory(
        email="test@gmail.com", password_hash="1234abcd", display_name="Test user"
    )
    db_session.add(user)
    await db_session.flush()
    await db_session.refresh(user)

    assert user.id is not None
    assert user.created_at is not None
    assert user.updated_at is not None
    assert user.is_active is True
    assert user.email == "test@gmail.com"
    assert user.password_hash == "1234abcd"
    assert user.display_name == "Test user"


@pytest.mark.asyncio
async def test_creating_users_with_duplicate_emails_raises_integrity_error(
    db_session: AsyncSession, user_factory
):
    user1 = user_factory(email="test1@gmail.com")
    user2 = user_factory(email="test1@gmail.com")
    db_session.add_all([user1, user2])

    with pytest.raises(IntegrityError):
        await db_session.flush()
