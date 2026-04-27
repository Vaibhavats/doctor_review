# middleware/auth_dependency.py  –  FastAPI "Depends" guard
from __future__ import annotations
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from bson import ObjectId

from config.database import get_users_collection
from middleware.jwt_handler import decode_token

bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> dict:
    """
    FastAPI dependency – attach the authenticated user dict to the request.
    Usage:  current_user: dict = Depends(get_current_user)
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authorised – no token provided",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        user_id = decode_token(credentials.credentials)
    except JWTError as exc:
        msg = (
            "Session expired – please login again"
            if "expired" in str(exc).lower()
            else "Invalid token – please login again"
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=msg,
            headers={"WWW-Authenticate": "Bearer"},
        )

    users = get_users_collection()
    user  = await users.find_one({"_id": ObjectId(user_id)})

    if not user or not user.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account not found or deactivated",
        )

    return user


def require_role(*roles: str):
    """Role-guard factory.  Usage:  Depends(require_role('admin'))"""
    async def _guard(current_user: dict = Depends(get_current_user)):
        if current_user.get("role") not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{current_user.get('role')}' is not authorised for this action",
            )
        return current_user
    return _guard
