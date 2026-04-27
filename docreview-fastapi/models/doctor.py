# models/doctor.py  –  MongoDB doctor document helpers
from __future__ import annotations
from datetime import datetime, timezone


def build_doctor_doc(data: dict) -> dict:
    """Build a new MongoDB doctor document from validated input."""
    now = datetime.now(timezone.utc)
    return {
        "name":             data["name"].strip(),
        "specialization":   data["specialization"].strip(),
        "department":       data["department"].strip(),
        "qualification":    data["qualification"].strip(),
        "experience_years": data["experience_years"],
        "bio":              data["bio"].strip(),
        "email":            data.get("email"),
        "phone":            data.get("phone"),
        "available_days":   data.get("available_days", ["Mon","Tue","Wed","Thu","Fri"]),
        "consultation_fee": data.get("consultation_fee"),
        "image_url":        data.get("image_url"),
        "avg_rating":       0.0,
        "total_reviews":    0,
        "is_active":        data.get("is_active", True),
        "created_at":       now,
        "updated_at":       now,
    }


def mongo_to_doctor_public(doc: dict) -> dict:
    """Convert a raw MongoDB doctor document to a public-safe dict."""
    return {
        "id":               str(doc["_id"]),
        "name":             doc["name"],
        "specialization":   doc["specialization"],
        "department":       doc["department"],
        "qualification":    doc["qualification"],
        "experience_years": doc.get("experience_years", 0),
        "bio":              doc.get("bio", ""),
        "email":            doc.get("email"),
        "phone":            doc.get("phone"),
        "available_days":   doc.get("available_days", []),
        "consultation_fee": doc.get("consultation_fee"),
        "image_url":        doc.get("image_url"),
        "avg_rating":       round(doc.get("avg_rating", 0.0), 1),
        "total_reviews":    doc.get("total_reviews", 0),
        "is_active":        doc.get("is_active", True),
        "created_at":       doc.get("created_at", datetime.now(timezone.utc)),
    }
