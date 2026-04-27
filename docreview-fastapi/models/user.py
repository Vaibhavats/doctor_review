# models/user.py  –  MongoDB document helpers + password hashing
from __future__ import annotations
from datetime import datetime, timezone
from passlib.context import CryptContext
from bson import ObjectId

# bcrypt context – 12 rounds for strong hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=12)


def hash_password(plain: str) -> str:
    plain = plain[:72] 
    return pwd_context.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def build_user_doc(name: str, email: str, password: str) -> dict:
    """Build a new MongoDB user document (password pre-hashed)."""
    now = datetime.now(timezone.utc)
    return {
        "name":        name.strip(),
        "email":       email.lower().strip(),
        "password":    hash_password(password),
        "role":        "patient",
        "is_active":   True,
        "last_login":  None,
        "login_count": 0,
        "created_at":  now,
        "updated_at":  now,
    }


def mongo_to_public(doc: dict) -> dict:
    """Convert a raw MongoDB document to a public-safe dict."""
    return {
        "id":          str(doc["_id"]),
        "name":        doc["name"],
        "email":       doc["email"],
        "role":        doc.get("role", "patient"),
        "created_at":  doc.get("created_at", datetime.now(timezone.utc)),
        "last_login":  doc.get("last_login"),
        "login_count": doc.get("login_count", 0),
    }
