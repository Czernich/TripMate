from pathlib import Path

from alembic.config import Config
from alembic.script import ScriptDirectory
from sqlalchemy import text

from app.database import SessionLocal


async def test_test_database_is_at_alembic_head():
    project_root = Path(__file__).resolve().parents[1]
    config = Config(str(project_root / "alembic.ini"))
    head_revision = ScriptDirectory.from_config(config).get_current_head()

    assert head_revision is not None

    async with SessionLocal() as session:
        result = await session.execute(text("SELECT version_num FROM alembic_version"))
        database_revision = result.scalar_one()

    assert database_revision == head_revision
