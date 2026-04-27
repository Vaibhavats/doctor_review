# 🏥 DocReview – Hospital Review System

A full-stack web application that allows patients to:

* Register & login securely (JWT Authentication)
* Browse doctors by department
* Verify appointments before submitting reviews
* Submit authentic reviews for doctors

---

## 🚀 Features

* 🔐 JWT Authentication (Login/Register)
* 👨‍⚕️ Doctor Listing API
* 📅 Appointment Verification System
* ⭐ Verified Review Submission
* 📊 Rating & Feedback System
* ⚡ FastAPI + MongoDB backend

---

## 🛠 Tech Stack

* **Backend:** FastAPI (Python)
* **Database:** MongoDB
* **Frontend:** HTML, CSS, JavaScript
* **Authentication:** JWT

---

## 📦 Project Structure

```
DoctorReview/
├── docreview-fastapi/
│   ├── config/
│   ├── controllers/
│   ├── routes/
│   ├── models/
│   └── main.py
├── frontend/
│   ├── index.html
│   └── auth.html
```

---

## ▶️ Run Locally

```bash
git clone https://github.com/Vaibhavats/doctor_review.git
cd DoctorReview/docreview-fastapi

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

uvicorn main:app --reload
```

Open API docs:

```
http://127.0.0.1:8000/docs
```

---

## 📸 Screenshots

![App Screenshot](https://github.com/user-attachments/assets/db4e8c6a-52fd-430c-9a83-3ee8e70cd901)

---

## 📌 Future Improvements

* 💳 Payment integration
* 🧑‍⚕️ Doctor dashboard
* 🌐 Deployment (Render / Vercel)
* 🤖 AI-based review analysis

---

## 👨‍💻 Author

**Vaibhav Kumar**
