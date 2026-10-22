import os

DEFAULT_DATABASE_URL = "sqlite:///./store.db"


def database_url() -> str:
    """Return the configured SQLAlchemy URL, defaulting to a local SQLite file."""
    return os.getenv("DATABASE_URL", DEFAULT_DATABASE_URL)
