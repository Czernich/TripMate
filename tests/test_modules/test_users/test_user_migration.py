import os
import subprocess
from pathlib import Path

import pytest
from sqlalchemy import inspect

from app.database import engine

PRE_USERS_REVISION = "44bc4bfbb1d2"


def run_alembic(*args: str) -> None:
    project_root = Path(__file__).resolve().parents[3]

    subprocess.run(
        ["alembic", *args], cwd=project_root, env=os.environ.copy(), check=True
    )


def get_table_schema(sync_connection, table_name: str) -> dict | None:
    inspector = inspect(sync_connection)
    if not inspector.has_table(table_name):
        return None
    columns = inspector.get_columns(table_name)

    return {
        "columns": sorted(
            (
                column["name"],
                str(column["type"]),
                column["nullable"],
            )
            for column in columns
        )
    }


@pytest.mark.migration
async def test_user_migration_preserves_trip_table(clean_migration_database) -> None:
    run_alembic("upgrade", PRE_USERS_REVISION)

    async with engine.connect() as connection:
        trip_before = await connection.run_sync(get_table_schema, "trips")
        users_before = await connection.run_sync(get_table_schema, "users")

    assert trip_before is not None
    assert users_before is None

    run_alembic("upgrade", "head")

    async with engine.connect() as connection:
        trip_after = await connection.run_sync(get_table_schema, "trips")
        users_after = await connection.run_sync(get_table_schema, "users")

    assert trip_after is not None
    assert users_after is not None
    assert trip_before == trip_after
