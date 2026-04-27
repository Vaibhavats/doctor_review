# models/doctor_schemas.py  –  Doctor request / response schemas
from __future__ import annotations
from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime


# ── Department enum values ────────────────────────────────────
DEPARTMENTS = [
    "Cardiology", "Neurology", "Orthopedics", "Pediatrics",
    "Gynecology", "Dermatology", "Oncology", "Ophthalmology",
    "ENT", "Psychiatry", "Radiology", "General Medicine",
]


# ── Create / Update (admin only) ─────────────────────────────
class DoctorCreate(BaseModel):
    name:            str            = Field(..., min_length=2, max_length=100,  examples=["Dr. Priya Sharma"])
    specialization:  str            = Field(..., min_length=2, max_length=100,  examples=["Senior Cardiologist"])
    department:      str            = Field(...,                                examples=["Cardiology"])
    qualification:   str            = Field(..., min_length=2, max_length=200,  examples=["MBBS, MD (Cardiology), DM"])
    experience_years: int           = Field(..., ge=0, le=60,                   examples=[12])
    bio:             str            = Field(..., min_length=10, max_length=1000, examples=["Experienced cardiologist..."])
    email:           Optional[str]  = Field(None,                               examples=["priya.sharma@gehosp.in"])
    phone:           Optional[str]  = Field(None,                               examples=["+91 98765 43210"])
    available_days:  List[str]      = Field(default=["Mon","Tue","Wed","Thu","Fri"],
                                           examples=[["Mon","Wed","Fri"]])
    consultation_fee: Optional[int] = Field(None, ge=0,                        examples=[500])
    image_url:       Optional[str]  = Field(None,                               examples=["https://..."])
    is_active:       bool           = True


class DoctorUpdate(BaseModel):
    name:             Optional[str]       = None
    specialization:   Optional[str]       = None
    department:       Optional[str]       = None
    qualification:    Optional[str]       = None
    experience_years: Optional[int]       = Field(None, ge=0, le=60)
    bio:              Optional[str]       = None
    email:            Optional[str]       = None
    phone:            Optional[str]       = None
    available_days:   Optional[List[str]] = None
    consultation_fee: Optional[int]       = Field(None, ge=0)
    image_url:        Optional[str]       = None
    is_active:        Optional[bool]      = None


# ── Public response ───────────────────────────────────────────
class DoctorPublic(BaseModel):
    id:               str
    name:             str
    specialization:   str
    department:       str
    qualification:    str
    experience_years: int
    bio:              str
    email:            Optional[str]  = None
    phone:            Optional[str]  = None
    available_days:   List[str]      = []
    consultation_fee: Optional[int]  = None
    image_url:        Optional[str]  = None
    avg_rating:       float          = 0.0
    total_reviews:    int            = 0
    is_active:        bool           = True
    created_at:       datetime

    model_config = {"from_attributes": True}


# ── List / paginated response ─────────────────────────────────
class DoctorListResponse(BaseModel):
    success:    bool         = True
    total:      int
    page:       int
    per_page:   int
    doctors:    List[DoctorPublic]


class DoctorDetailResponse(BaseModel):
    success: bool         = True
    doctor:  DoctorPublic


class DoctorCreateResponse(BaseModel):
    success: bool         = True
    message: str
    doctor:  DoctorPublic


class DepartmentsResponse(BaseModel):
    success:     bool      = True
    departments: List[str]
