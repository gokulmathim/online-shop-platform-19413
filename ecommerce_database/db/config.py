import os
from dotenv import load_dotenv

# Load environment variables from .env if present
load_dotenv()

def _str_to_bool(value: str) -> bool:
    return str(value).lower() in {"1", "true", "yes", "y", "on"}

# PUBLIC_INTERFACE
def get_database_url() -> str:
    """Get the SQLAlchemy database URL from environment variables."""
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        raise RuntimeError("DATABASE_URL environment variable is required for ecommerce_database.")
    return db_url

# PUBLIC_INTERFACE
def get_sql_echo() -> bool:
    """Whether to echo SQL statements."""
    return _str_to_bool(os.getenv("SQL_ECHO", "false"))
