# config/database.py  –  MongoDB collections, indexes, and seed data
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import IndexModel, ASCENDING, DESCENDING, TEXT
from config.settings import get_settings
import logging

logger   = logging.getLogger("docreview")
settings = get_settings()

_client: AsyncIOMotorClient | None = None


def get_client() -> AsyncIOMotorClient:
    global _client
    if _client is None:
        _client = AsyncIOMotorClient(
            settings.mongo_uri,
            serverSelectionTimeoutMS=5000,
            socketTimeoutMS=45_000,
        )
    return _client


def get_db():
    return get_client()[settings.mongo_db_name]

def get_users_collection():        return get_db()["users"]
def get_doctors_collection():      return get_db()["doctors"]
def get_reviews_collection():      return get_db()["reviews"]
def get_appointments_collection(): return get_db()["appointments"]


# ── Startup ────────────────────────────────────────────────────
async def connect_db():
    client = get_client()
    try:
        await client.admin.command("ping")
        logger.info("✅  MongoDB Atlas connected  →  %s", settings.mongo_db_name)

        # Users
        await get_users_collection().create_indexes([
            IndexModel([("email", ASCENDING)], unique=True, name="users_email_unique"),
        ])

        # Doctors
        await get_doctors_collection().create_indexes([
            IndexModel([("department", ASCENDING)], name="docs_dept"),
            IndexModel([("is_active",  ASCENDING)], name="docs_active"),
            IndexModel([("avg_rating", DESCENDING)], name="docs_rating"),
            IndexModel(
                [("name", TEXT), ("specialization", TEXT), ("department", TEXT)],
                name="docs_text",
            ),
        ])

        # Reviews – one review per patient per doctor (enforced here + in controller)
        await get_reviews_collection().create_indexes([
            IndexModel([("doctor_id", ASCENDING), ("patient_id", ASCENDING)],
                       unique=True, name="rev_one_per_patient"),
            IndexModel([("doctor_id", ASCENDING), ("is_approved", ASCENDING)],
                       name="rev_by_doctor"),
            IndexModel([("appointment_id", ASCENDING)], name="rev_appt"),
        ])

        # Appointments – appointment_id must be globally unique
        await get_appointments_collection().create_indexes([
            IndexModel([("appointment_id", ASCENDING)], unique=True, name="appt_id_unique"),
            IndexModel([("doctor_id", ASCENDING)],      name="appt_doctor"),
            IndexModel([("patient_email", ASCENDING)],  name="appt_patient"),
        ])

        logger.info("📑  Indexes verified")

        await seed_doctors_if_empty()
        await seed_appointments_if_empty()

    except Exception as exc:
        logger.error("❌  MongoDB connection failed: %s", exc)
        raise


async def close_db():
    global _client
    if _client:
        _client.close()
        _client = None
        logger.info("🔌  MongoDB connection closed")


# ── Seed doctors ───────────────────────────────────────────────
async def seed_doctors_if_empty():
    from datetime import datetime, timezone
    col = get_doctors_collection()
    if await col.count_documents({}) > 0:
        return

    now = datetime.now(timezone.utc)
    doctors = [
        {
            "name": "Dr. Priya Sharma", "specialization": "Senior Cardiologist",
            "department": "Cardiology",
            "qualification": "MBBS, MD (Cardiology), DM (Interventional Cardiology)",
            "experience_years": 14,
            "bio": "Dr. Priya Sharma is a highly experienced interventional cardiologist with 14 years of practice. She specialises in coronary artery disease, heart failure, and cardiac rehabilitation, with over 2,000 successful interventional procedures.",
            "email": "priya.sharma@gehosp.in", "phone": "+91 98765 43210",
            "available_days": ["Mon","Tue","Wed","Thu","Fri"],
            "consultation_fee": 800, "image_url": None,
            "avg_rating": 4.9, "total_reviews": 0, "is_active": True,
            "created_at": now, "updated_at": now,
        },
        {
            "name": "Dr. Anil Mehta", "specialization": "Chief Neurologist",
            "department": "Neurology",
            "qualification": "MBBS, MD (Medicine), DM (Neurology)",
            "experience_years": 18,
            "bio": "Dr. Anil Mehta leads the Neurology department with 18 years of experience. He specialises in epilepsy, stroke, multiple sclerosis, and neurodegenerative disorders with a patient-first approach.",
            "email": "anil.mehta@gehosp.in", "phone": "+91 98765 43211",
            "available_days": ["Mon","Wed","Fri"],
            "consultation_fee": 900, "image_url": None,
            "avg_rating": 4.7, "total_reviews": 0, "is_active": True,
            "created_at": now, "updated_at": now,
        },
        {
            "name": "Dr. Sunita Rawat", "specialization": "Orthopedic Surgeon",
            "department": "Orthopedics",
            "qualification": "MBBS, MS (Orthopedics), Fellowship in Joint Replacement",
            "experience_years": 11,
            "bio": "Dr. Sunita Rawat specialises in joint replacement, sports injuries, and spine surgery with over 1,500 successful knee and hip replacements using minimally invasive techniques.",
            "email": "sunita.rawat@gehosp.in", "phone": "+91 98765 43212",
            "available_days": ["Tue","Thu","Sat"],
            "consultation_fee": 750, "image_url": None,
            "avg_rating": 4.8, "total_reviews": 0, "is_active": True,
            "created_at": now, "updated_at": now,
        },
        {
            "name": "Dr. Rajan Gupta", "specialization": "Pediatric Specialist",
            "department": "Pediatrics",
            "qualification": "MBBS, MD (Pediatrics), Fellowship in Neonatology",
            "experience_years": 9,
            "bio": "Dr. Rajan Gupta is a compassionate pediatrician and neonatologist with 9 years of experience in childhood infections, growth disorders, and neonatal intensive care.",
            "email": "rajan.gupta@gehosp.in", "phone": "+91 98765 43213",
            "available_days": ["Mon","Tue","Wed","Thu","Fri","Sat"],
            "consultation_fee": 600, "image_url": None,
            "avg_rating": 4.6, "total_reviews": 0, "is_active": True,
            "created_at": now, "updated_at": now,
        },
        {
            "name": "Dr. Kavita Negi", "specialization": "Consultant Dermatologist",
            "department": "Dermatology",
            "qualification": "MBBS, MD (Dermatology, Venereology & Leprosy)",
            "experience_years": 8,
            "bio": "Dr. Kavita Negi specialises in medical and cosmetic dermatology including psoriasis, eczema, acne, hair loss, laser therapy, and skin rejuvenation.",
            "email": "kavita.negi@gehosp.in", "phone": "+91 98765 43214",
            "available_days": ["Mon","Wed","Fri","Sat"],
            "consultation_fee": 700, "image_url": None,
            "avg_rating": 4.5, "total_reviews": 0, "is_active": True,
            "created_at": now, "updated_at": now,
        },
        {
            "name": "Dr. Mohan Tiwari", "specialization": "Senior Oncologist",
            "department": "Oncology",
            "qualification": "MBBS, MD (Internal Medicine), DM (Medical Oncology)",
            "experience_years": 20,
            "bio": "Dr. Mohan Tiwari brings 20 years of cancer care expertise in medical oncology, chemotherapy protocols, and palliative care, supporting patients and families throughout treatment.",
            "email": "mohan.tiwari@gehosp.in", "phone": "+91 98765 43215",
            "available_days": ["Mon","Tue","Thu","Fri"],
            "consultation_fee": 1000, "image_url": None,
            "avg_rating": 4.8, "total_reviews": 0, "is_active": True,
            "created_at": now, "updated_at": now,
        },
        {
            "name": "Dr. Anjali Singh", "specialization": "Gynaecologist & Obstetrician",
            "department": "Gynecology",
            "qualification": "MBBS, MS (Obstetrics & Gynaecology)",
            "experience_years": 13,
            "bio": "Dr. Anjali Singh specialises in high-risk pregnancies, laparoscopic surgery, and reproductive health with 13 years of experience helping thousands of women through safe pregnancies.",
            "email": "anjali.singh@gehosp.in", "phone": "+91 98765 43216",
            "available_days": ["Mon","Tue","Wed","Thu","Fri"],
            "consultation_fee": 750, "image_url": None,
            "avg_rating": 4.9, "total_reviews": 0, "is_active": True,
            "created_at": now, "updated_at": now,
        },
        {
            "name": "Dr. Vikram Joshi", "specialization": "Ophthalmologist",
            "department": "Ophthalmology",
            "qualification": "MBBS, MS (Ophthalmology), FRCS",
            "experience_years": 16,
            "bio": "Dr. Vikram Joshi is a leading ophthalmologist with expertise in cataract surgery, glaucoma, and LASIK, with over 5,000 successful eye surgeries and excellent post-operative outcomes.",
            "email": "vikram.joshi@gehosp.in", "phone": "+91 98765 43217",
            "available_days": ["Tue","Wed","Thu","Sat"],
            "consultation_fee": 700, "image_url": None,
            "avg_rating": 4.7, "total_reviews": 0, "is_active": True,
            "created_at": now, "updated_at": now,
        },
    ]
    await col.insert_many(doctors)
    logger.info("🌱  Seeded %d doctors", len(doctors))


# ── Seed sample appointments ───────────────────────────────────
async def seed_appointments_if_empty():
    """
    Seed demo appointment IDs so testers can try the review flow immediately.
    Format:  GEH-YYYY-NNNNN
    These link patient emails to doctors by appointment_id.
    """
    from datetime import datetime, timezone
    col = get_appointments_collection()
    if await col.count_documents({}) > 0:
        return

    # Fetch inserted doctor IDs
    docs_col = get_doctors_collection()
    doctors  = await docs_col.find({}, {"_id": 1, "name": 1}).to_list(length=20)
    if not doctors:
        return

    now   = datetime.now(timezone.utc)
    seeds = []
    # Create 2–3 demo appointments per doctor
    demo_patients = [
        "demo@gehosp.in",
        "test@gehosp.in",
        "patient@gehosp.in",
    ]
    counter = 1
    for doc in doctors:
        for pidx, email in enumerate(demo_patients[:2]):
            appt_id = f"GEH-2026-{counter:05d}"
            seeds.append({
                "appointment_id":   appt_id,
                "doctor_id":        str(doc["_id"]),
                "doctor_name":      doc["name"],
                "patient_email":    email,
                "appointment_date": now,
                "notes":            "Demo appointment for testing",
                "is_used":          False,
                "created_at":       now,
                "updated_at":       now,
            })
            counter += 1

    try:
        await col.insert_many(seeds, ordered=False)
        logger.info("🌱  Seeded %d demo appointments (use GEH-2026-00001 to GEH-2026-%05d)", len(seeds), counter-1)
    except Exception as e:
        logger.warning("Appointment seed skipped (likely duplicates): %s", e)
