from logging.config import fileConfig

from alembic import context
from sqlalchemy import Connection, text

from tremor_api.config import DB_SCHEMA, DatabaseSettings
from tremor_api.db import build_engine
from tremor_api.models import Base

config = context.config
if config.config_file_name and not config.attributes.get("connection"):
    fileConfig(config.config_file_name)


def run_migrations(connection: Connection) -> None:
    connection.execute(text(f'CREATE SCHEMA IF NOT EXISTS "{DB_SCHEMA}"'))
    context.configure(
        connection=connection,
        target_metadata=Base.metadata,
        version_table_schema=DB_SCHEMA,
        include_schemas=True,
        include_name=lambda name, type_, _: type_ != "schema" or name == DB_SCHEMA,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connection = config.attributes.get("connection")
    if connection is not None:
        run_migrations(connection)
        return
    engine = build_engine(DatabaseSettings())
    with engine.begin() as conn:
        run_migrations(conn)
    engine.dispose()


if context.is_offline_mode():
    raise SystemExit("offline migrations are not supported; run against a live database")
run_migrations_online()
