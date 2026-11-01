import sys
import os

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy import select
from app.core.config import settings
from app.core.security import hash_password
from app.database.base import Base
from app.database.connection import SessionLocal, engine
from app.models.admin import AdminUser, RoleEnum


def seed_database():
    """Seed initial administrative accounts for testing and demonstration."""
    print("=" * 70)
    print("CYNBIT TECHNOLOGIES — DATABASE BOOTSTRAP & SEEDER")
    print("=" * 70)

    # Ensure tables exist
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        # 1. Seed Super Admin
        superadmin_email = settings.INITIAL_SUPERADMIN_EMAIL
        stmt = select(AdminUser).where(AdminUser.email == superadmin_email)
        existing_superadmin = db.scalar(stmt)

        if not existing_superadmin:
            superadmin = AdminUser(
                email=superadmin_email,
                full_name=settings.INITIAL_SUPERADMIN_NAME,
                hashed_password=hash_password(settings.INITIAL_SUPERADMIN_PASSWORD),
                role=RoleEnum.SUPER_ADMIN,
                is_active=True
            )
            db.add(superadmin)
            print(f"[+] Created SUPER_ADMIN: {superadmin_email} | Password: {settings.INITIAL_SUPERADMIN_PASSWORD}")
        else:
            print(f"[*] SUPER_ADMIN already exists: {superadmin_email}")

        # 2. Seed Inquiry Reviewer (Staff / Read-Only / Status Update)
        reviewer_email = "reviewer@cynbit.in"
        reviewer_password = "Reviewer@Cynbit2026!"
        stmt_rev = select(AdminUser).where(AdminUser.email == reviewer_email)
        existing_reviewer = db.scalar(stmt_rev)

        if not existing_reviewer:
            reviewer = AdminUser(
                email=reviewer_email,
                full_name="Cynbit Inquiry Reviewer",
                hashed_password=hash_password(reviewer_password),
                role=RoleEnum.INQUIRY_REVIEWER,
                is_active=True
            )
            db.add(reviewer)
            print(f"[+] Created INQUIRY_REVIEWER: {reviewer_email} | Password: {reviewer_password}")
        else:
            print(f"[*] INQUIRY_REVIEWER already exists: {reviewer_email}")

        db.commit()
        print("[OK] Database seeding completed successfully.")

    except Exception as e:
        db.rollback()
        print(f"[!] Error during database seeding: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
