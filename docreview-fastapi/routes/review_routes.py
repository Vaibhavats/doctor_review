# routes/review_routes.py  –  /api/reviews  &  /api/appointments
# from __future__ import annotations
from fastapi import APIRouter, Depends, Query, Request
from slowapi import Limiter
from slowapi.util import get_remote_address

from models.review_schemas import (
    AppointmentCreate, AppointmentVerifyRequest,
    AppointmentVerifyResponse, ReviewCreate,
    ReviewListResponse, ReviewCreateResponse,
)
from controllers.review_controller import (
    create_appointment, verify_appointment,
    submit_review, list_reviews, list_demo_appointments,
)
from middleware.auth_dependency import get_current_user, require_role

router  = APIRouter(tags=["Reviews & Appointments"])
limiter = Limiter(key_func=get_remote_address)


# ── POST /api/appointments  (admin: create appointment) ───────
@router.post(
    "/api/appointments",
    status_code=201,
    summary="Create appointment record  [Admin only]",
)
async def appointment_create(
    data:       AppointmentCreate,
    admin_user: dict = Depends(require_role("admin")),
):
    return await create_appointment(data, admin_user)


# ── POST /api/appointments/verify  (patient: verify before review) ─
@router.post(
    "/api/appointments/verify",
    response_model=AppointmentVerifyResponse,
    summary="Verify appointment ID before submitting a review",
)
@limiter.limit("20/minute")
async def appointment_verify(
    request:      Request,
    data:         AppointmentVerifyRequest,
    current_user: dict = Depends(get_current_user),
):
    return await verify_appointment(data, current_user)


# ── GET /api/appointments/mine  (patient: list their unused appts for a doctor) ─
@router.get(
    "/api/appointments/mine",
    summary="List my unused appointment IDs for a doctor",
)
async def my_appointments(
    doctor_id:    str  = Query(...),
    current_user: dict = Depends(get_current_user),
):
    return await list_demo_appointments(doctor_id, current_user)


# ── POST /api/reviews  (patient: submit review) ───────────────
@router.post(
    "/api/reviews",
    response_model=ReviewCreateResponse,
    status_code=201,
    summary="Submit a doctor review (requires valid appointment ID)",
)
@limiter.limit("10/minute")
async def review_submit(
    request:      Request,
    data:         ReviewCreate,
    current_user: dict = Depends(get_current_user),
):
    return await submit_review(data, current_user)


# ── GET /api/reviews  (public: list reviews for a doctor) ─────
@router.get(
    "/api/reviews",
    response_model=ReviewListResponse,
    summary="Get approved reviews for a doctor",
)
async def reviews_list(
    doctor_id: str = Query(..., description="Doctor's MongoDB ObjectId"),
    page:      int = Query(1,  ge=1),
    per_page:  int = Query(10, ge=1, le=50),
):
    return await list_reviews(doctor_id, page, per_page)
