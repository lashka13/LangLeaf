from logging.config import fileConfig

from sqlalchemy.ext.asyncio import create_async_engine
from alembic import context
import asyncio
from backend.models import Base

config = context.config

from dotenv import load_dotenv
import os

# Load environment variables from .env
load_dotenv()

# Get database URL from .env
db_url = os.getenv("DATABASE_URL")

target_metadata = Base.metadata

if Base.metadata.tables:
    print("✅ MetaData tables detected:", Base.metadata.tables.keys())
else:
    print("❌ No tables found in MetaData!")

if db_url:
    config.set_main_option("sqlalchemy.url", db_url)

def run_migrations_online():
    """Run migrations in 'online' mode with async support."""
    connectable = create_async_engine(db_url)

    async def do_migrations():
        async with connectable.connect() as connection:
            await connection.run_sync(run_migrations)

    def run_migrations(connection):
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()

    asyncio.run(do_migrations())

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()