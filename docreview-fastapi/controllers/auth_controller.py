# controllers/auth_controller.py  –  Register / Login / Me / Logout
from __future__ import annotations
from datetime import datetime, timezone

from fastapi import HTTPException, status
from pymongo.errors import DuplicateKeyError
from bson import ObjectId

from config.database import get_users_collection
from models.schemas import RegisterRequest, LoginRequest, AuthResponse, MeResponse, SuccessResponse, UserPublic
from models.user import build_user_doc, verify_password, mongo_to_public
from middleware.jwt_handler import create_access_token


# ══════════════════════════════════════════════════════════════
#  POST  /api/auth/register
# ══════════════════════════════════════════════════════════════
async def register_user(data: RegisterRequest) -> AuthResponse:
    users = get_users_collection()

    # Explicit duplicate check for a friendlier message
    existing = await users.find_one({"email": data.email.lower().strip()})
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "success": False,
                "field":   "email",
                "message": "An account with this email already exists. Please login instead.",
            },
        )

    doc = build_user_doc(data.name, data.email, data.password)

    try:
        result = await users.insert_one(doc)
    except DuplicateKeyError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "success": False,
                "field":   "email",
                "message": "An account with this email already exists.",
            },
        )

    doc["_id"] = result.inserted_id
    token      = create_access_token(str(result.inserted_id))

    return AuthResponse(
        success=True,
        message=f"Account created successfully! Welcome to DocReview, {data.name}.",
        token=token,
        user=UserPublic(**mongo_to_public(doc)),
    )


# ══════════════════════════════════════════════════════════════
#  POST  /api/auth/login
# ══════════════════════════════════════════════════════════════
async def login_user(data: LoginRequest) -> AuthResponse:
    users = get_users_collection()

    user = await users.find_one({"email": data.email.lower().strip()})

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "success": False,
                "field":   "email",
                "message": "No account found with this email address.",
            },
        )

    if not user.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "success": False,
                "message": "This account has been deactivated. Please contact support.",
            },
        )

    if not verify_password(data.password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "success": False,
                "field":   "password",
                "message": "Incorrect password. Please try again.",
            },
        )

    # Update login metadata (fire-and-forget – don't block response)
    now = datetime.now(timezone.utc)
    await users.update_one(
        {"_id": user["_id"]},
        {
            "$set":  {"last_login": now, "updated_at": now},
            "$inc":  {"login_count": 1},
        },
    )
    user["last_login"]  = now
    user["login_count"] = user.get("login_count", 0) + 1

    token = create_access_token(str(user["_id"]))

    return AuthResponse(
        success=True,
        message=f"Welcome back, {user['name']}!",
        token=token,
        user=UserPublic(**mongo_to_public(user)),
    )


# ══════════════════════════════════════════════════════════════
#  GET  /api/auth/me   (protected)
# ══════════════════════════════════════════════════════════════
async def get_me(current_user: dict) -> MeResponse:
    return MeResponse(
        success=True,
        user=UserPublic(**mongo_to_public(current_user)),
    )


# ══════════════════════════════════════════════════════════════
#  POST  /api/auth/logout  (protected)
# ══════════════════════════════════════════════════════════════
async def logout_user(current_user: dict) -> SuccessResponse:
    # JWT is stateless – client simply discards the token.
    # For production, maintain a token-denylist in Redis here.
    return SuccessResponse(success=True, message="Logged out successfully.")
