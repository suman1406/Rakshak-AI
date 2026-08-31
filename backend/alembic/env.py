from logging.config import fileConfig
from alembic import context
from sqlalchemy import create_engine
from app.core.config import settings
from app.db.base import Base
from app.models import farm, identity, video, prediction, verification, governance  # noqa: F401

config = context.config
if config.config_file_name:
    fileConfig(config.config_file_name)
target_metadata = Base.metadata

def _sync_url() -> str:
    # Alembic is synchronous. Keep the installed psycopg v3 driver instead of
    # stripping it (which makes SQLAlchemy select unavailable psycopg2).
    return settings.DATABASE_URL.replace("+asyncpg", "+psycopg").replace("+aiosqlite", "")

def run_migrations_offline() -> None:
    context.configure(url=_sync_url(), target_metadata=target_metadata, literal_binds=True, compare_type=True)
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    connectable = create_engine(_sync_url(), pool_pre_ping=True)
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata, compare_type=True)
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
