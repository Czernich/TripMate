import hashlib
import secrets

from pydantic import TypeAdapter

from app.models.user import User
from app.modules.users.exceptions import UserNotFoundException
from app.modules.users.repository import UserRepository
from app.modules.users.schemas import NormalizedEmail, UserCreate


class UserService:
    def __init__(self, repository: UserRepository):
        self.repository = repository

    @staticmethod
    def _hash_password(password: str) -> str:
        salt = secrets.token_bytes(16)

        password_hash = hashlib.scrypt(
            password.encode("utf-8"),
            salt=salt,
            n=2**14,
            r=8,
            p=1,
            dklen=64,
        )

        return f"scrypt$16384$8$1${salt.hex()}${password_hash.hex()}"

    async def create_user(self, payload: UserCreate) -> User:
        user = User(
            email=payload.email,
            display_name=payload.display_name,
            password_hash=self._hash_password(payload.password),
        )

        return await self.repository.add(user)

    async def get_user_by_id(self, user_id: int) -> User:
        user = await self.repository.get_by_id(user_id)

        if user is None:
            raise UserNotFoundException()

        return user

    async def get_user_by_email(self, email: str) -> User:
        normalized_email = TypeAdapter(NormalizedEmail).validate_python(email)

        user = await self.repository.get_by_email(str(normalized_email))

        if user is None:
            raise UserNotFoundException()

        return user
