# models/review_schemas.py  –  Appointment & Review schemas
from __future__ import annotations
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator


# ══════════════════════════════════════════════════════════════
#  APPOINTMENT  (used to verify patient before review)
# ══════════════════════════════════════════════════════════════
class AppointmentCreate(BaseModel):
    """Admin creates appointments; patients use the ID to unlock reviews."""
    appointment_id: str   = Field(..., min_length=4, max_length=30,
                                   examples=["GEH-2026-00123"])
    doctor_id:      str   = Field(..., examples=["664abc123..."])
    patient_email:  str   = Field(..., examples=["rohit@example.com"])
    appointment_date: Optional[datetime] = None
    notes:          Optional[str] = None


class AppointmentPublic(BaseModel):
    id:               str
    appointment_id:   str
    doctor_id:        str
    doctor_name:      str
    patient_email:    str
    appointment_date: Optional[datetime] = None
    is_used:          bool   = False   # True once review is submitted
    created_at:       datetime


class AppointmentVerifyRequest(BaseModel):
    """Patient submits this to verify their appointment before reviewing."""
    appointment_id: str = Field(..., min_length=1, examples=["GEH-2026-00123"])
    doctor_id:      str = Field(..., examples=["664abc123..."])


class AppointmentVerifyResponse(BaseModel):
    success:        bool
    valid:          bool
    message:        str
    appointment_id: Optional[str] = None
    doctor_name:    Optional[str] = None
    already_reviewed: bool = False


# ══════════════════════════════════════════════════════════════
#  REVIEW
# ══════════════════════════════════════════════════════════════
class ReviewCreate(BaseModel):
    doctor_id:      str = Field(..., examples=["664abc123..."])
    appointment_id: str = Field(..., min_length=1, examples=["GEH-2026-00123"])
    rating:         int = Field(..., ge=1, le=5,   examples=[5])
    title:          str = Field(..., min_length=3, max_length=120,
                                 examples=["Excellent doctor, very thorough"])
    feedback:       str = Field(..., min_length=10, max_length=1500,
                                 examples=["Dr. Sharma was very attentive..."])
    is_anonymous:   bool = False

    @field_validator("rating")
    @classmethod
    def valid_rating(cls, v: int) -> int:
        if not 1 <= v <= 5:
            raise ValueError("Rating must be between 1 and 5")
        return v


class ReviewPublic(BaseModel):
    id:             str
    doctor_id:      str
    doctor_name:    str
    patient_name:   str          # "Anonymous" if is_anonymous
    patient_id:     str
    rating:         int
    title:          str
    feedback:       str
    is_anonymous:   bool
    is_approved:    bool
    created_at:     datetime


class ReviewListResponse(BaseModel):
    success:  bool = True
    total:    int
    page:     int
    per_page: int
    avg_rating: float
    reviews:  List[ReviewPublic]


class ReviewCreateResponse(BaseModel):
    success: bool = True
    message: str
    review:  ReviewPublic
