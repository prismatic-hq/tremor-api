from collections.abc import Iterator
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from pydantic import SecretStr
from sqlalchemy import Engine, text
from testcontainers.community.postgres import PostgresContainer

from tests.steward_stub import StewardStub, running_steward_stub
from tremor_api.config import DatabaseSettings, StewardSettings
from tremor_api.db import build_engine
from tremor_api.main import create_app

REPO_ROOT = Path(__file__).resolve().parents[2]
POSTGRES_IMAGE = "postgres:17-alpine"


@pytest.fixture(scope="session")
def db_settings() -> Iterator[DatabaseSettings]:
    with PostgresContainer(POSTGRES_IMAGE, driver="psycopg") as postgres:
        yield DatabaseSettings(
            host=postgres.get_container_host_ip(),
            port=int(postgres.get_exposed_port(5432)),
            name=postgres.dbname,
            user=postgres.username,
            password=SecretStr(postgres.password),
        )


@pytest.fixture(scope="session")
def engine(db_settings: DatabaseSettings) -> Iterator[Engine]:
    engine = build_engine(db_settings)
    alembic_config = Config(str(REPO_ROOT / "alembic.ini"))
    with engine.begin() as connection:
        alembic_config.attributes["connection"] = connection
        command.upgrade(alembic_config, "head")
    yield engine
    engine.dispose()


@pytest.fixture
def steward() -> Iterator[StewardStub]:
    with running_steward_stub() as stub:
        yield stub


@pytest.fixture
def client(
    engine: Engine, db_settings: DatabaseSettings, steward: StewardStub
) -> Iterator[TestClient]:
    with engine.begin() as connection:
        connection.execute(text("TRUNCATE tremor.alerts"))
    steward_settings = StewardSettings(url=steward.url, timeout_seconds=0.5)
    with TestClient(create_app(db_settings, steward_settings)) as test_client:
        yield test_client
