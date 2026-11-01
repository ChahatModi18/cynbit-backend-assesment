from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.core.config import settings

# Engine configuration with dialect-specific optimizations
engine_kwargs = {
    "echo": settings.DEBUG,
}

if settings.is_sqlite:
    # SQLite requires check_same_thread=False for multithreaded FastAPI access
    engine_kwargs["connect_args"] = {"check_same_thread": False}
else:
    # MySQL 8.0+ production connection pool tuning
    engine_kwargs.update({
        "pool_size": settings.DB_POOL_SIZE,
        "max_overflow": settings.DB_MAX_OVERFLOW,
        "pool_recycle": settings.DB_POOL_RECYCLE,
        "pool_pre_ping": settings.DB_POOL_PRE_PING,
    })

engine = create_engine(settings.DATABASE_URL, **engine_kwargs)

# Session factory for generating independent database sessions per request
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False,
)


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency that yields a database session per HTTP request
    and ensures clean closure upon request completion.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

