# middleware/jwt_handler.py  –  JWT create / decode helpers
from __future__ import annotations
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from config.settings import get_settings

settings = get_settings()


def create_access_token(user_id: str) -> str:
    """Create a signed JWT containing the user's MongoDB ObjectId."""
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.access_token_expire_minutes
    )
    payload = {
        "sub": user_id,
        "exp": expire,
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_token(token: str) -> str:
    """Decode & validate a JWT.  Returns the user_id (sub claim).
    Raises JWTError on invalid / expired tokens.
    """
    payload = jwt.decode(
        token,
        settings.jwt_secret,
        algorithms=[settings.jwt_algorithm],
    )
    user_id: str | None = payload.get("sub")
    if user_id is None:
        raise JWTError("Token payload missing 'sub'")
    return user_id
