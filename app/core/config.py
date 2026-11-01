from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application Settings managed via environment variables and .env file.
    Follows 12-factor application methodology.
    """
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=True,
    )

    # Project Information
    PROJECT_NAME: str = "Cynbit Technologies — Secure Inquiry API"
    VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/api/v1"
    ENVIRONMENT: str = "development"
    DEBUG: bool = False

    # Server Configuration
    HOST: str = "127.0.0.1"
    PORT: int = 8000

    # Cryptography & JWT Security
    # MUST be overridden in production via environment variable JWT_SECRET_KEY
    JWT_SECRET_KEY: str = "cynbit-dev-insecure-secret-key-32-chars-minimum-required!!"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # CORS Allowed Origins (Comma-separated string in .env, parsed into list)
    CORS_ORIGINS: str = (
        "http://localhost:3000,"
        "https://cynbit.in,"
        "https://www.cynbit.in,"
        "https://portal.cynbit.in"
    )

    # Database Configuration
    # Defaults to SQLite for immediate, zero-friction local run/testing;
    # In production, set to: mysql+pymysql://user:password@localhost:3306/cynbit_db
    DATABASE_URL: str = "sqlite:///./cynbit_inquiries.db"
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20
    DB_POOL_RECYCLE: int = 1800
    DB_POOL_PRE_PING: bool = True

    # Initial Super Admin Seed (Optional for bootstrapping)
    INITIAL_SUPERADMIN_EMAIL: str = "admin@cynbit.in"
    INITIAL_SUPERADMIN_PASSWORD: str = "Admin@Cynbit2026!"
    INITIAL_SUPERADMIN_NAME: str = "Cynbit Lead Architect"

    @property
    def cors_origins_list(self) -> List[str]:
        """Parse comma-separated CORS_ORIGINS string into a list of origins."""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    @property
    def is_sqlite(self) -> bool:
        """Helper to determine if the active database is SQLite."""
        return self.DATABASE_URL.startswith("sqlite")


# Global Singleton Settings Instance
settings = Settings()

