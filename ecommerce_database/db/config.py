import os
import logging
from dotenv import load_dotenv

# Load environment variables from .env if present
load_dotenv()

logger = logging.getLogger(__name__)

def _str_to_bool(value: str) -> bool:
    return str(value).lower() in {"1", "true", "yes", "y", "on"}

# PUBLIC_INTERFACE
def get_database_url() -> str:
    """Get the SQLAlchemy database URL from environment variables.

    If DATABASE_URL is not provided, default to a local SQLite database file
    to allow the application to start in development/CI environments.
    This default is safe for local/testing but should be overridden in production.
    """
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        # Default to a local SQLite file in the project directory
        default_sqlite = "sqlite:///./ecommerce.db"
        logger.warning(
            "DATABASE_URL not set. Falling back to local SQLite database at %s. "
            "For production, set DATABASE_URL to your database connection string.",
            default_sqlite,
        )
        return default_sqlite
    return db_url

# PUBLIC_INTERFACE
def get_sql_echo() -> bool:
    """Whether to echo SQL statements."""
    return _str_to_bool(os.getenv("SQL_ECHO", "false"))
