# controllers/doctor_controller.py  –  Doctor CRUD + search + pagination
from __future__ import annotations
from datetime import datetime, timezone
from typing import Optional

from bson import ObjectId
from fastapi import HTTPException, status

from config.database import get_doctors_collection
from models.doctor_schemas import (
    DoctorCreate, DoctorUpdate,
    DoctorListResponse, DoctorDetailResponse,
    DoctorCreateResponse, DepartmentsResponse,
    DEPARTMENTS,
)
from models.doctor import build_doctor_doc, mongo_to_doctor_public


# ── Helper ────────────────────────────────────────────────────
def _not_found(doctor_id: str):
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail={"success": False, "message": f"Doctor with id '{doctor_id}' not found."},
    )


# ══════════════════════════════════════════════════════════════
#  GET  /api/doctors
#  Query params: department, search, page, per_page, sort_by
# ══════════════════════════════════════════════════════════════
async def list_doctors(
    department: Optional[str] = None,
    search:     Optional[str] = None,
    page:       int = 1,
    per_page:   int = 12,
    sort_by:    str = "avg_rating",   # avg_rating | experience_years | name | total_reviews
) -> DoctorListResponse:

    col    = get_doctors_collection()
    query: dict = {"is_active": True}

    # Department filter
    if department and department.lower() != "all":
        query["department"] = {"$regex": f"^{department}$", "$options": "i"}

    # Full-text search OR regex on name/specialization
    if search and search.strip():
        s = search.strip()
        query["$or"] = [
            {"name":           {"$regex": s, "$options": "i"}},
            {"specialization": {"$regex": s, "$options": "i"}},
            {"department":     {"$regex": s, "$options": "i"}},
            {"qualification":  {"$regex": s, "$options": "i"}},
        ]

    # Sort mapping
    sort_map = {
        "avg_rating":       [("avg_rating", -1), ("total_reviews", -1)],
        "experience_years": [("experience_years", -1)],
        "name":             [("name", 1)],
        "total_reviews":    [("total_reviews", -1)],
    }
    sort_order = sort_map.get(sort_by, sort_map["avg_rating"])

    # Pagination
    skip    = (page - 1) * per_page
    total   = await col.count_documents(query)
    cursor  = col.find(query).sort(sort_order).skip(skip).limit(per_page)
    docs    = await cursor.to_list(length=per_page)

    return DoctorListResponse(
        success=True,
        total=total,
        page=page,
        per_page=per_page,
        doctors=[mongo_to_doctor_public(d) for d in docs],   # type: ignore[arg-type]
    )


# ══════════════════════════════════════════════════════════════
#  GET  /api/doctors/{doctor_id}
# ══════════════════════════════════════════════════════════════
async def get_doctor(doctor_id: str) -> DoctorDetailResponse:
    if not ObjectId.is_valid(doctor_id):
        _not_found(doctor_id)

    col  = get_doctors_collection()
    doc  = await col.find_one({"_id": ObjectId(doctor_id), "is_active": True})
    if not doc:
        _not_found(doctor_id)

    return DoctorDetailResponse(
        success=True,
        doctor=mongo_to_doctor_public(doc),   # type: ignore[arg-type]
    )


# ══════════════════════════════════════════════════════════════
#  GET  /api/doctors/departments
# ══════════════════════════════════════════════════════════════
async def get_departments() -> DepartmentsResponse:
    col   = get_doctors_collection()
    depts = await col.distinct("department", {"is_active": True})
    return DepartmentsResponse(success=True, departments=sorted(depts))


# ══════════════════════════════════════════════════════════════
#  POST  /api/doctors          (admin only)
# ══════════════════════════════════════════════════════════════
async def create_doctor(data: DoctorCreate, admin_user: dict) -> DoctorCreateResponse:
    col = get_doctors_collection()
    doc = build_doctor_doc(data.model_dump())

    result = await col.insert_one(doc)
    doc["_id"] = result.inserted_id

    return DoctorCreateResponse(
        success=True,
        message=f"Doctor '{data.name}' added successfully.",
        doctor=mongo_to_doctor_public(doc),   # type: ignore[arg-type]
    )


# ══════════════════════════════════════════════════════════════
#  PUT  /api/doctors/{doctor_id}   (admin only)
# ══════════════════════════════════════════════════════════════
async def update_doctor(doctor_id: str, data: DoctorUpdate, admin_user: dict) -> DoctorDetailResponse:
    if not ObjectId.is_valid(doctor_id):
        _not_found(doctor_id)

    col    = get_doctors_collection()
    update = {k: v for k, v in data.model_dump().items() if v is not None}
    if not update:
        raise HTTPException(status_code=400, detail={"success": False, "message": "No fields to update."})

    update["updated_at"] = datetime.now(timezone.utc)
    result = await col.find_one_and_update(
        {"_id": ObjectId(doctor_id)},
        {"$set": update},
        return_document=True,
    )
    if not result:
        _not_found(doctor_id)

    return DoctorDetailResponse(success=True, doctor=mongo_to_doctor_public(result))   # type: ignore[arg-type]


# ══════════════════════════════════════════════════════════════
#  DELETE  /api/doctors/{doctor_id}   (admin only – soft delete)
# ══════════════════════════════════════════════════════════════
async def delete_doctor(doctor_id: str, admin_user: dict):
    if not ObjectId.is_valid(doctor_id):
        _not_found(doctor_id)

    col = get_doctors_collection()
    result = await col.find_one_and_update(
        {"_id": ObjectId(doctor_id)},
        {"$set": {"is_active": False, "updated_at": datetime.now(timezone.utc)}},
    )
    if not result:
        _not_found(doctor_id)

    return {"success": True, "message": "Doctor deactivated successfully."}
