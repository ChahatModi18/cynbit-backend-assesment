import os
import sys
import pytest
from typing import Generator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

# Ensure project root is available in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.config import settings
from app.core.security import create_access_token, hash_password
from app.database.base import Base
from app.database.connection import get_db
from app.main import app
from app.models.admin import AdminUser, RoleEnum
from app.models.inquiry import Inquiry, InquiryAuditLog, InquiryStatusEnum

# Isolated in-memory SQLite engine for tests with thread-sharing pool
TEST_DATABASE_URL = "sqlite:///:memory:"
test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """Create all database tables once for the test session and tear down at conclusion."""
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def db_session() -> Generator[Session, None, None]:
    """Provide a clean database session per test with automatic rollback / cleanup."""
    connection = test_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    # Seed baseline administrator accounts
    superadmin = AdminUser(
        email="admin@cynbit.in",
        full_name="Lead SuperAdmin",
        hashed_password=hash_password("Admin@Cynbit2026!"),
        role=RoleEnum.SUPER_ADMIN,
        is_active=True
    )
    reviewer = AdminUser(
        email="reviewer@cynbit.in",
        full_name="Inquiry Reviewer",
        hashed_password=hash_password("Reviewer@Cynbit2026!"),
        role=RoleEnum.INQUIRY_REVIEWER,
        is_active=True
    )
    session.add_all([superadmin, reviewer])
    session.commit()

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(db_session: Session) -> Generator[TestClient, None, None]:
    """Provide a FastAPI TestClient with the get_db dependency overridden to the test session."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def superadmin_token() -> str:
    """Issue a valid signed JWT for SuperAdmin testing."""
    return create_access_token(
        subject=1,
        role=RoleEnum.SUPER_ADMIN.value,
        email="admin@cynbit.in"
    )


@pytest.fixture
def reviewer_token() -> str:
    """Issue a valid signed JWT for InquiryReviewer testing."""
    return create_access_token(
        subject=2,
        role=RoleEnum.INQUIRY_REVIEWER.value,
        email="reviewer@cynbit.in"
    )


@pytest.fixture
def auth_headers_superadmin(superadmin_token: str) -> dict:
    return {"Authorization": f"Bearer {superadmin_token}"}


@pytest.fixture
def auth_headers_reviewer(reviewer_token: str) -> dict:
    return {"Authorization": f"Bearer {reviewer_token}"}


@pytest.fixture
def sample_inquiry(db_session: Session) -> Inquiry:
    """Seed a sample inquiry record in the test database."""
    inq = Inquiry(
        name="Vikram Mehta",
        email="vikram@example.com",
        company="Mehta Logistics",
        subject="Fleet Automation Systems",
        message="Interested in deploying automated logistics pipelines and route optimization.",
        status=InquiryStatusEnum.PENDING
    )
    db_session.add(inq)
    db_session.flush()

    audit = InquiryAuditLog(
        inquiry_id=inq.id,
        admin_user_id=None,
        action="CREATED",
        old_status=None,
        new_status=InquiryStatusEnum.PENDING.value,
        notes="Test seed inquiry"
    )
    db_session.add(audit)
    db_session.commit()
    db_session.refresh(inq)
    return inq

