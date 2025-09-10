from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase, scoped_session
from .config import get_database_url, get_sql_echo

# Base class for declarative models
class Base(DeclarativeBase):
    pass

# Create engine based on env config
engine = create_engine(get_database_url(), echo=get_sql_echo(), future=True)

# Thread-local/session-local scoped session
SessionLocal = scoped_session(sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True))

# PUBLIC_INTERFACE
def get_session():
    """Yield a SQLAlchemy session. Use in 'with' blocks or ensure close() is called."""
    return SessionLocal()
