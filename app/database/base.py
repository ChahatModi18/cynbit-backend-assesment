from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """
    SQLAlchemy 2.x Declarative Base.
    All ORM models inherit from this base class for metadata and table registry.
    """
    pass

