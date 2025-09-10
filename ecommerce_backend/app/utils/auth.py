from dataclasses import dataclass
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, create_refresh_token
from typing import Any, Dict


# PUBLIC_INTERFACE
def hash_password(password: str) -> str:
    """Hash a plain-text password securely."""
    return generate_password_hash(password)


# PUBLIC_INTERFACE
def verify_password(password: str, password_hash: str) -> bool:
    """Verify a plain-text password against a stored hash."""
    return check_password_hash(password_hash, password)


@dataclass
class JwtTokens:
    access_token: str
    refresh_token: str


# PUBLIC_INTERFACE
def create_tokens(identity: Dict[str, Any]) -> JwtTokens:
    """Create JWT access and refresh tokens for identity."""
    access = create_access_token(identity=identity)
    refresh = create_refresh_token(identity=identity)
    return JwtTokens(access_token=access, refresh_token=refresh)
