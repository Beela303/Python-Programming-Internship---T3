from sqlalchemy import Engine, create_engine, event
from sqlalchemy.orm import Session, sessionmaker

from relational_store.config import database_url
from relational_store.models import Base


def make_engine(url: str | None = None) -> Engine:
    """Create an engine and enable SQLite foreign-key constraints."""
    engine = create_engine(url or database_url(), echo=False)

    if engine.dialect.name == "sqlite":
        @event.listens_for(engine, "connect")
        def enable_foreign_keys(dbapi_connection, _connection_record) -> None:
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

    return engine


def create_schema(url: str | None = None) -> Engine:
    """Create tables for demos/tests. Use Alembic migrations for schema evolution."""
    engine = make_engine(url)
    Base.metadata.create_all(engine)
    return engine


def make_session_factory(engine: Engine) -> sessionmaker[Session]:
    """Return a factory; callers decide the lifetime of each session."""
    return sessionmaker(bind=engine, expire_on_commit=False)
