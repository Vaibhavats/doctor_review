# routes/auth_routes.py  –  /api/auth/*

from fastapi import APIRouter, Depends, Request, Body
from typing import Annotated
from slowapi import Limiter
from slowapi.util import get_remote_address

from models.schemas import (
    RegisterRequest, LoginRequest,
    AuthResponse, MeResponse, SuccessResponse,
)
from controllers.auth_controller import (
    register_user, login_user, get_me, logout_user,
)
from middleware.auth_dependency import get_current_user

router = APIRouter(prefix="/api/auth", tags=["Authentication"])
limiter = Limiter(key_func=get_remote_address)


# ── POST /api/auth/register ───────────────────────────────────
@router.post(
    "/register",
    response_model=AuthResponse,
    status_code=201,
    summary="Register a new patient account",
)
@limiter.limit("10/15minutes")
async def register(
    request: Request,
    data: Annotated[RegisterRequest, Body()]
):
    return await register_user(data)


# ── POST /api/auth/login ─────────────────────────────────────
@router.post(
    "/login",
    response_model=AuthResponse,
    status_code=200,
    summary="Login and receive a JWT",
)
@limiter.limit("10/15minutes")
async def login(
    request: Request,
    data: Annotated[LoginRequest, Body()]
):
    return await login_user(data)


# ── GET /api/auth/me  (protected) ────────────────────────────
@router.get(
    "/me",
    response_model=MeResponse,
    status_code=200,
    summary="Get currently authenticated user",
)
async def me(current_user: dict = Depends(get_current_user)):
    return await get_me(current_user)


# ── POST /api/auth/logout  (protected) ───────────────────────
@router.post(
    "/logout",
    response_model=SuccessResponse,
    status_code=200,
    summary="Logout",
)
async def logout(current_user: dict = Depends(get_current_user)):
    return await logout_user(current_user)