# 🏥 DocReview – Graphic Era Hospital | FastAPI + MongoDB Atlas Backend

A production-ready **Python FastAPI + MongoDB Atlas** authentication backend for the DocReview patient review platform.

---

## 📁 Project Structure

```
docreview-fastapi/
├── main.py                         # FastAPI app entry point
├── requirements.txt                # Python dependencies
├── .env.example                    # Environment variables template
├── .gitignore
├── README.md
│
├── config/
│   ├── __init__.py
│   ├── settings.py                 # Pydantic settings (reads .env)
│   └── database.py                 # Async Motor (MongoDB) connection
│
├── models/
│   ├── __init__.py
│   ├── schemas.py                  # Pydantic request/response schemas
│   └── user.py                     # DB document helpers + bcrypt
│
├── middleware/
│   ├── __init__.py
│   ├── jwt_handler.py              # JWT create / decode
│   └── auth_dependency.py          # FastAPI Depends() guard
│
├── controllers/
│   ├── __init__.py
│   └── auth_controller.py          # Register / Login / Me / Logout logic
│
├── routes/
│   ├── __init__.py
│   └── auth_routes.py              # /api/auth/* router + rate limiting
│
└── public/
    ├── auth.html                   # Frontend (calls FastAPI on :8000)
    └── index.html                  # Landing page (redirected to after login)
```

---

## 🚀 Step-by-Step Setup

### Step 1 — Install Python 3.11+
```bash
python --version   # must be 3.11 or higher
```
Download from https://python.org if needed.

---

### Step 2 — Create a virtual environment
```bash
cd docreview-fastapi

# Create venv
python -m venv venv

# Activate it:
# Windows:
venv\Scripts\activate

# Mac / Linux:
source venv/bin/activate
```

---

### Step 3 — Install dependencies
```bash
pip install -r requirements.txt
```

---

### Step 4 — Set Up MongoDB Atlas (Free)

1. Go to https://www.mongodb.com/atlas/database → **Try Free**
2. Create a **Free M0 cluster** (any region)
3. **Security → Database Access** → Add user:
   - Username: `docreview_user`
   - Password: (generate and save it)
   - Role: **Read and write to any database**
4. **Security → Network Access** → **Allow access from anywhere** (`0.0.0.0/0`)
5. **Deployment → Database** → **Connect** → **Drivers** → copy the connection string:
   ```
   mongodb+srv://docreview_user:<password>@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority
   ```

---

### Step 5 — Configure .env
```bash
cp .env.example .env
```

Edit `.env`:
```env
MONGO_URI=mongodb+srv://docreview_user:YOUR_PASSWORD@cluster0.xxxxx.mongodb.net/docreview_db?retryWrites=true&w=majority
JWT_SECRET=generate_this_with_python_-c_import_secrets_print_secrets_token_hex_32
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080
APP_HOST=0.0.0.0
APP_PORT=8000
CLIENT_ORIGIN=http://127.0.0.1:5500
ENVIRONMENT=development
```

Generate a strong JWT secret:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

---

### Step 6 — Run the server
```bash
python main.py
```

Expected output:
```
🏥  DocReview – Graphic Era Hospital
─────────────────────────────────────────────
🚀  FastAPI starting on  http://0.0.0.0:8000
🌍  Environment:         development
📡  API docs:            http://localhost:8000/docs
✅  MongoDB Atlas connected  →  docreview_db
📑  Indexes verified
```

---

### Step 7 — Open the Frontend

**Option A – VS Code Live Server:**
1. Open project folder in VS Code
2. Right-click `public/auth.html` → **Open with Live Server**
3. Opens at `http://127.0.0.1:5500/auth.html`

**Option B – Directly via FastAPI:**
1. Visit `http://localhost:8000/auth.html`

**Option C – Open index.html from browser:**
- Click Login / Register → goes to `auth.html`
- After login → redirects back to `index.html`

---

## 🔌 API Reference

| Method | Endpoint               | Auth          | Description                      |
|--------|------------------------|:-------------:|----------------------------------|
| POST   | `/api/auth/register`   | ❌ Public     | Register new patient             |
| POST   | `/api/auth/login`      | ❌ Public     | Login → JWT token                |
| GET    | `/api/auth/me`         | ✅ Bearer JWT | Get current user profile         |
| POST   | `/api/auth/logout`     | ✅ Bearer JWT | Logout (client discards token)   |
| GET    | `/api/health`          | ❌ Public     | Health check                     |
| GET    | `/docs`                | ❌ Public     | **Swagger UI** (interactive!)    |
| GET    | `/redoc`               | ❌ Public     | ReDoc API documentation          |

---

## 🧪 Test with Swagger UI

1. Open http://localhost:8000/docs
2. Click **POST /api/auth/register** → **Try it out** → fill fields → **Execute**
3. Click **POST /api/auth/login** → execute → copy the `token` from response
4. Click **Authorize** (top right) → paste `Bearer <your_token>` → Authorize
5. Now test **GET /api/auth/me** — you'll see your profile

---

## 🧪 Test with curl

```bash
# Register
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"name":"Rohit Bisht","email":"rohit@example.com","password":"mypass123"}'

# Login (copy token from response)
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"rohit@example.com","password":"mypass123"}'

# Get profile (replace TOKEN)
curl http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer TOKEN"
```

---

## 🗄️ MongoDB Document (what gets stored)

```json
{
  "_id": "ObjectId(665abc...)",
  "name": "Rohit Bisht",
  "email": "rohit@example.com",
  "password": "$2b$12$hashed_with_bcrypt...",
  "role": "patient",
  "is_active": true,
  "last_login": "2026-03-28T10:30:00Z",
  "login_count": 3,
  "created_at": "2026-03-20T08:00:00Z",
  "updated_at": "2026-03-28T10:30:00Z"
}
```

Password is **never** stored in plain text.

---

## 🔐 Security Features

| Feature | Detail |
|---------|--------|
| Passwords | bcrypt (12 salt rounds) |
| Authentication | JWT HS256, 7-day expiry |
| Rate limiting | 10 requests / 15 min per IP (slowapi) |
| Input validation | Pydantic v2 + email-validator |
| CORS | Whitelisted origins only |
| Duplicate prevention | Unique MongoDB index on `email` |

---

## 🆘 Troubleshooting

| Problem | Fix |
|---------|-----|
| `ServerSelectionTimeoutError` | Check `MONGO_URI` in `.env`; whitelist your IP in Atlas |
| `CORS error in browser` | Add your frontend URL to `CLIENT_ORIGIN` in `.env` |
| `401 Unauthorized` | Token expired — login again |
| `422 Unprocessable Entity` | Validation failed — check request body |
| `Address already in use` | Change `APP_PORT` in `.env` |
| Module not found | Activate venv: `source venv/bin/activate` |

---

© 2026 DocReview – Graphic Era Hospital
