# models/review.py  –  MongoDB document helpers for reviews & appointments
from __future__ import annotations
from datetime import datetime, timezone


def build_appointment_doc(data: dict) -> dict:
    now = datetime.now(timezone.utc)
    return {
        "appointment_id":   data["appointment_id"].strip().upper(),
        "doctor_id":        data["doctor_id"],
        "doctor_name":      data.get("doctor_name", ""),
        "patient_email":    data["patient_email"].lower().strip(),
        "appointment_date": data.get("appointment_date"),
        "notes":            data.get("notes"),
        "is_used":          False,   # becomes True once reviewed
        "created_at":       now,
        "updated_at":       now,
    }


def build_review_doc(
    doctor_id: str,
    doctor_name: str,
    patient_id: str,
    patient_name: str,
    appointment_id: str,
    rating: int,
    title: str,
    feedback: str,
    is_anonymous: bool = False,
) -> dict:
    now = datetime.now(timezone.utc)
    return {
        "doctor_id":      doctor_id,
        "doctor_name":    doctor_name,
        "patient_id":     patient_id,
        "patient_name":   patient_name,
        "appointment_id": appointment_id.strip().upper(),
        "rating":         rating,
        "title":          title.strip(),
        "feedback":       feedback.strip(),
        "is_anonymous":   is_anonymous,
        "is_approved":    True,   # auto-approve; set False for admin moderation
        "created_at":     now,
        "updated_at":     now,
    }


def mongo_to_review_public(doc: dict, is_anonymous: bool = False) -> dict:
    return {
        "id":           str(doc["_id"]),
        "doctor_id":    doc["doctor_id"],
        "doctor_name":  doc["doctor_name"],
        "patient_name": "Anonymous" if doc.get("is_anonymous") else doc.get("patient_name", "Patient"),
        "patient_id":   str(doc.get("patient_id", "")),
        "rating":       doc["rating"],
        "title":        doc["title"],
        "feedback":     doc["feedback"],
        "is_anonymous": doc.get("is_anonymous", False),
        "is_approved":  doc.get("is_approved", True),
        "created_at":   doc.get("created_at", datetime.now(timezone.utc)),
    }


def mongo_to_appointment_public(doc: dict) -> dict:
    return {
        "id":               str(doc["_id"]),
        "appointment_id":   doc["appointment_id"],
        "doctor_id":        doc["doctor_id"],
        "doctor_name":      doc.get("doctor_name", ""),
        "patient_email":    doc["patient_email"],
        "appointment_date": doc.get("appointment_date"),
        "is_used":          doc.get("is_used", False),
        "created_at":       doc.get("created_at", datetime.now(timezone.utc)),
    }
