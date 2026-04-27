# routes/doctor_routes.py  –  /api/doctors/*
from __future__ import annotations
from typing import Optional

from fastapi import APIRouter, Depends, Query, Request
from slowapi import Limiter
from slowapi.util import get_remote_address

from models.doctor_schemas import (
    DoctorCreate, DoctorUpdate,
    DoctorListResponse, DoctorDetailResponse,
    DoctorCreateResponse, DepartmentsResponse,
)
from controllers.doctor_controller import (
    list_doctors, get_doctor, get_departments,
    create_doctor, update_doctor, delete_doctor,
)
from middleware.auth_dependency import get_current_user, require_role

router  = APIRouter(prefix="/api/doctors", tags=["Doctors"])
limiter = Limiter(key_func=get_remote_address)


# ── GET /api/doctors/departments  (must be before /{id}) ─────
@router.get(
    "/departments",
    response_model=DepartmentsResponse,
    summary="Get all active departments",
)
async def departments():
    return await get_departments()


# ── GET /api/doctors ─────────────────────────────────────────
@router.get(
    "",
    response_model=DoctorListResponse,
    summary="List doctors with optional filters & pagination",
)
@limiter.limit("60/minute")
async def doctors_list(
    request:    Request,
    department: Optional[str] = Query(None,  description="Filter by department name"),
    search:     Optional[str] = Query(None,  description="Search name, specialization, department"),
    page:       int           = Query(1,     ge=1,  description="Page number"),
    per_page:   int           = Query(12,    ge=1, le=50, description="Results per page"),
    sort_by:    str           = Query("avg_rating",
                                      description="Sort: avg_rating | experience_years | name | total_reviews"),
):
    return await list_doctors(department, search, page, per_page, sort_by)


# ── GET /api/doctors/{doctor_id} ─────────────────────────────
@router.get(
    "/{doctor_id}",
    response_model=DoctorDetailResponse,
    summary="Get full doctor profile by ID",
)
async def doctor_detail(doctor_id: str):
    return await get_doctor(doctor_id)


# ── POST /api/doctors   (admin only) ─────────────────────────
@router.post(
    "",
    response_model=DoctorCreateResponse,
    status_code=201,
    summary="Add a new doctor  [Admin only]",
)
async def doctor_create(
    data:       DoctorCreate,
    admin_user: dict = Depends(require_role("admin")),
):
    return await create_doctor(data, admin_user)


# ── PUT /api/doctors/{doctor_id}   (admin only) ──────────────
@router.put(
    "/{doctor_id}",
    response_model=DoctorDetailResponse,
    summary="Update doctor details  [Admin only]",
)
async def doctor_update(
    doctor_id:  str,
    data:       DoctorUpdate,
    admin_user: dict = Depends(require_role("admin")),
):
    return await update_doctor(doctor_id, data, admin_user)


# ── DELETE /api/doctors/{doctor_id}   (admin only) ───────────
@router.delete(
    "/{doctor_id}",
    summary="Deactivate a doctor  [Admin only]",
)
async def doctor_delete(
    doctor_id:  str,
    admin_user: dict = Depends(require_role("admin")),
):
    return await delete_doctor(doctor_id, admin_user)
