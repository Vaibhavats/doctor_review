# controllers/review_controller.py
from __future__ import annotations
from datetime import datetime, timezone

from bson import ObjectId
from fastapi import HTTPException, status

from config.database import (
    get_reviews_collection,
    get_appointments_collection,
    get_doctors_collection,
)
from models.review_schemas import (
    AppointmentCreate, AppointmentVerifyRequest, AppointmentVerifyResponse,
    ReviewCreate, ReviewListResponse, ReviewCreateResponse, ReviewPublic,
    AppointmentPublic,
)
from models.review import (
    build_appointment_doc, build_review_doc,
    mongo_to_review_public, mongo_to_appointment_public,
)


# ══════════════════════════════════════════════════════════════
#  POST /api/appointments          (admin creates)
# ══════════════════════════════════════════════════════════════
async def create_appointment(data: AppointmentCreate, admin_user: dict) -> dict:
    col = get_appointments_collection()

    # Validate doctor exists
    if not ObjectId.is_valid(data.doctor_id):
        raise HTTPException(status_code=400, detail={"success": False, "message": "Invalid doctor ID."})

    doctor = await get_doctors_collection().find_one({"_id": ObjectId(data.doctor_id)})
    if not doctor:
        raise HTTPException(status_code=404, detail={"success": False, "message": "Doctor not found."})

    doc = build_appointment_doc(data.model_dump())
    doc["doctor_name"] = doctor["name"]

    try:
        result = await col.insert_one(doc)
        doc["_id"] = result.inserted_id
        return {
            "success": True,
            "message": f"Appointment {doc['appointment_id']} created.",
            "appointment": mongo_to_appointment_public(doc),
        }
    except Exception:
        raise HTTPException(
            status_code=409,
            detail={"success": False, "message": f"Appointment ID '{data.appointment_id}' already exists."},
        )


# ══════════════════════════════════════════════════════════════
#  POST /api/appointments/verify   (patient verifies before review)
# ══════════════════════════════════════════════════════════════
async def verify_appointment(
    data: AppointmentVerifyRequest,
    current_user: dict,
) -> AppointmentVerifyResponse:

    appt_col   = get_appointments_collection()
    review_col = get_reviews_collection()

    appt_id_upper = data.appointment_id.strip().upper()

    # Find the appointment
    appt = await appt_col.find_one({
        "appointment_id": appt_id_upper,
        "doctor_id":      data.doctor_id,
    })

    if not appt:
        return AppointmentVerifyResponse(
            success=True,
            valid=False,
            message="No appointment found with this ID for the selected doctor. Please check and try again.",
        )

    # Check patient email matches
    if appt["patient_email"].lower() != current_user["email"].lower():
        return AppointmentVerifyResponse(
            success=True,
            valid=False,
            message="This appointment ID does not match your registered email address.",
        )

    # Check if already reviewed
    existing_review = await review_col.find_one({
        "doctor_id":  data.doctor_id,
        "patient_id": str(current_user["_id"]),
    })
    if existing_review:
        return AppointmentVerifyResponse(
            success=True,
            valid=False,
            message="You have already submitted a review for this doctor.",
            already_reviewed=True,
            doctor_name=appt.get("doctor_name", ""),
        )

    # Check appointment already used for a review
    if appt.get("is_used"):
        return AppointmentVerifyResponse(
            success=True,
            valid=False,
            message="This appointment ID has already been used to submit a review.",
            already_reviewed=True,
        )

    return AppointmentVerifyResponse(
        success=True,
        valid=True,
        message="Appointment verified! You may now submit your review.",
        appointment_id=appt_id_upper,
        doctor_name=appt.get("doctor_name", ""),
    )


# ══════════════════════════════════════════════════════════════
#  POST /api/reviews               (patient submits review)
# ══════════════════════════════════════════════════════════════
async def submit_review(data: ReviewCreate, current_user: dict) -> ReviewCreateResponse:
    appt_col   = get_appointments_collection()
    review_col = get_reviews_collection()
    doc_col    = get_doctors_collection()

    if not ObjectId.is_valid(data.doctor_id):
        raise HTTPException(status_code=400, detail={"success": False, "message": "Invalid doctor ID."})

    # ── 1. Validate appointment ───────────────────────────────
    appt_id_upper = data.appointment_id.strip().upper()
    appt = await appt_col.find_one({
        "appointment_id": appt_id_upper,
        "doctor_id":      data.doctor_id,
    })

    if not appt:
        raise HTTPException(
            status_code=400,
            detail={"success": False, "field": "appointment_id",
                    "message": "Invalid appointment ID for this doctor. Please verify first."},
        )

    if appt["patient_email"].lower() != current_user["email"].lower():
        raise HTTPException(
            status_code=403,
            detail={"success": False, "message": "This appointment does not belong to your account."},
        )

    if appt.get("is_used"):
        raise HTTPException(
            status_code=409,
            detail={"success": False, "message": "This appointment has already been used for a review."},
        )

    # ── 2. One review per patient per doctor ──────────────────
    existing = await review_col.find_one({
        "doctor_id":  data.doctor_id,
        "patient_id": str(current_user["_id"]),
    })
    if existing:
        raise HTTPException(
            status_code=409,
            detail={"success": False, "message": "You have already reviewed this doctor."},
        )

    # ── 3. Fetch doctor ───────────────────────────────────────
    doctor = await doc_col.find_one({"_id": ObjectId(data.doctor_id)})
    if not doctor:
        raise HTTPException(status_code=404, detail={"success": False, "message": "Doctor not found."})

    # ── 4. Insert review ──────────────────────────────────────
    review_doc = build_review_doc(
        doctor_id=data.doctor_id,
        doctor_name=doctor["name"],
        patient_id=str(current_user["_id"]),
        patient_name=current_user["name"],
        appointment_id=appt_id_upper,
        rating=data.rating,
        title=data.title,
        feedback=data.feedback,
        is_anonymous=data.is_anonymous,
    )

    result = await review_col.insert_one(review_doc)
    review_doc["_id"] = result.inserted_id

    # ── 5. Mark appointment as used ───────────────────────────
    await appt_col.update_one(
        {"_id": appt["_id"]},
        {"$set": {"is_used": True, "updated_at": datetime.now(timezone.utc)}},
    )

    # ── 6. Recalculate doctor's avg_rating ────────────────────
    pipeline = [
        {"$match": {"doctor_id": data.doctor_id, "is_approved": True}},
        {"$group": {"_id": None, "avg": {"$avg": "$rating"}, "count": {"$sum": 1}}},
    ]
    agg = await review_col.aggregate(pipeline).to_list(length=1)
    if agg:
        await doc_col.update_one(
            {"_id": ObjectId(data.doctor_id)},
            {"$set": {
                "avg_rating":   round(agg[0]["avg"], 1),
                "total_reviews": agg[0]["count"],
                "updated_at":   datetime.now(timezone.utc),
            }},
        )

    return ReviewCreateResponse(
        success=True,
        message="Your review has been submitted successfully. Thank you for your feedback!",
        review=ReviewPublic(**mongo_to_review_public(review_doc)),
    )


# ══════════════════════════════════════════════════════════════
#  GET /api/reviews?doctor_id=...  (public listing)
# ══════════════════════════════════════════════════════════════
async def list_reviews(
    doctor_id: str,
    page:      int = 1,
    per_page:  int = 10,
) -> ReviewListResponse:

    col   = get_reviews_collection()
    query = {"doctor_id": doctor_id, "is_approved": True}
    total = await col.count_documents(query)

    skip   = (page - 1) * per_page
    cursor = col.find(query).sort("created_at", -1).skip(skip).limit(per_page)
    docs   = await cursor.to_list(length=per_page)

    # avg
    pipeline = [
        {"$match": query},
        {"$group": {"_id": None, "avg": {"$avg": "$rating"}}},
    ]
    agg = await col.aggregate(pipeline).to_list(length=1)
    avg = round(agg[0]["avg"], 1) if agg else 0.0

    return ReviewListResponse(
        success=True,
        total=total,
        page=page,
        per_page=per_page,
        avg_rating=avg,
        reviews=[ReviewPublic(**mongo_to_review_public(d)) for d in docs],
    )


# ══════════════════════════════════════════════════════════════
#  GET /api/appointments/demo      (helper – list demo IDs)
# ══════════════════════════════════════════════════════════════
async def list_demo_appointments(doctor_id: str, current_user: dict) -> dict:
    """Returns appointment IDs belonging to the logged-in user for a doctor."""
    col   = get_appointments_collection()
    query = {
        "doctor_id":    doctor_id,
        "patient_email": current_user["email"].lower(),
        "is_used":       False,
    }
    cursor = col.find(query, {"appointment_id": 1, "doctor_name": 1}).limit(5)
    appts  = await cursor.to_list(length=5)
    return {
        "success": True,
        "appointments": [
            {"appointment_id": a["appointment_id"], "doctor_name": a.get("doctor_name", "")}
            for a in appts
        ],
    }
