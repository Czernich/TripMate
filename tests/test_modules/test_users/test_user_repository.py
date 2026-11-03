import pytest
from sqlalchemy import select

from app.modules.users.exceptions import UserAlreadyExistsException
from app.modules.users.repository import UserRepository


@pytest.mark.asyncio
async def test_add_user(db_session, user_factory):
    repository = UserRepository(db_session)
    user = user_factory()

    result = await repository.add(user)

    assert result.id is not None
    assert result.email == user.email
    assert result.display_name == user.display_name
    assert result.password_hash == user.password_hash


@pytest.mark.asyncio
async def test_get_by_id(db_session, saved_user):
    repository = UserRepository(db_session)

    result = await repository.get_by_id(saved_user.id)

    assert result is not None
    assert result.id == saved_user.id


@pytest.mark.asyncio
async def test_get_by_id_not_found(db_session):
    repository = UserRepository(db_session)

    result = await repository.get_by_id(999999)

    assert result is None


@pytest.mark.asyncio
async def test_get_by_email(db_session, saved_user):
    repository = UserRepository(db_session)

    result = await repository.get_by_email(saved_user.email)

    assert result is not None
    assert result.id == saved_user.id


@pytest.mark.asyncio
async def test_get_by_email_not_found(db_session):
    repository = UserRepository(db_session)

    result = await repository.get_by_email("missing@example.com")

    assert result is None


@pytest.mark.asyncio
async def test_add_duplicate_email(
    db_session,
    saved_user,
    user_factory,
):
    repository = UserRepository(db_session)

    duplicate = user_factory(email=saved_user.email)

    with pytest.raises(UserAlreadyExistsException):
        await repository.add(duplicate)


@pytest.mark.asyncio
async def test_session_usable_after_duplicate_email(
    db_session,
    saved_user,
    user_factory,
):
    repository = UserRepository(db_session)

    duplicate = user_factory(email=saved_user.email)

    with pytest.raises(UserAlreadyExistsException):
        await repository.add(duplicate)

    result = await db_session.execute(select(1))

    assert result.scalar_one() == 1
