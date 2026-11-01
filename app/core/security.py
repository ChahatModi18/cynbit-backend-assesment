from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional, Union
import bcrypt
import jwt
from app.core.config import settings


def hash_password(plain_password: str) -> str:
    """
    Hash a plaintext password using bcrypt with a recommended work factor of 12.
    Salt is generated automatically.
    """
    salt = bcrypt.gensalt(rounds=12)
    hashed_bytes = bcrypt.hashpw(plain_password.encode("utf-8"), salt)
    return hashed_bytes.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plaintext password against a bcrypt hashed password string.
    Safely returns False if decoding or verification fails.
    """
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            hashed_password.encode("utf-8")
        )
    except Exception:
        return False


def create_access_token(
    subject: Union[str, int],
    role: str,
    email: str,
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Generate a cryptographically signed JSON Web Token (JWT) with standard claims:
    - sub: Subject identifier (User ID)
    - role: User Role for RBAC
    - email: User email
    - exp: Expiration timestamp (UTC)
    - iat: Issued at timestamp (UTC)
    """
    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode: Dict[str, Any] = {
        "sub": str(subject),
        "role": role,
        "email": email,
        "exp": expire,
        "iat": now,
        "iss": "cynbit-auth-service"
    }

    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


def decode_access_token(token: str) -> Dict[str, Any]:
    """
    Decode and verify the signature, expiration, and claims of a JWT access token.
    Raises jwt.PyJWTError subclasses upon invalid signature or expired token.
    """
    payload = jwt.decode(
        token,
        settings.JWT_SECRET_KEY,
        algorithms=[settings.JWT_ALGORITHM],
        options={"require": ["exp", "sub", "role"]}
    )
    return payload

