# Nutrivize - Full Documentation

## 1. Overview

Nutrivize is a FastAPI-based backend application for tracking users' daily food consumption, logging nutritional intake, and providing admin-level analytics. It supports user authentication and role-based access control with a clean, modular architecture.

---

## 2. Project Structure

```
Nutrition_Logger/
├── .env
├── pyproject.toml
├── README.md
├── backend/
│   ├── main.py             # FastAPI app setup
│   ├── config.py           # Pydantic config via .env
│   ├── server.py           # Uvicorn app runner
│   ├── api/                # FastAPI route modules
│   │   ├── auth/           # Custom JWT authentication logic
│   │   ├── dependancies.py
│   │   ├── routes/
│   │       ├── admin.py
│   │       ├── auth.py
│   │       ├── daily_log.py
│   │       ├── food.py
│   │       ├── food_entry.py
│   │       └── user.py
│   ├── crud/               # Reusable CRUD logic
│   ├── database/db.py      # SQLAlchemy engine/session
│   ├── models/             # ORM models
│   └── schemas/            # Pydantic request/response schemas
└── tests/                  # Endpoint and integration tests
```

---

## 3. Configuration

The `.env` file manages sensitive config:

```env
POSTGRES_USER=your_user
POSTGRES_PW=your_password
POSTGRES_DB=nutrition_db
POSTGRES_TEST_DB=nutrition_test
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
PGADMIN_EMAIL=admin@example.com
PGADMIN_PW=adminpass
SECRET_KEY=supersecretkey
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
ENV=dev
```

---

## 4. Models Overview

### User

* `id`: Primary key
* `username`, `email`: Unique
* `hashed_password`: Secure password
* `role`: Either `user` or `admin`

### Food

* Nutritional info per serving: `calories`, `protein`, `carbs`, `fat`

### DailyLog

* One per user per day
* Linked to multiple food entries

### FoodEntry

* Quantity of specific food in a log

---

## 5. API Endpoints

### Authentication - `/auth`

* `POST /register` → Register new user
* `POST /login` → Get JWT token
* `POST /refresh` → Refresh token
* `POST /logout` → Clear token cookie
* `GET /me` → Current user info

### Users - `/users`

* `GET /` → List users (admin only)
* `GET /{id}` → User by ID
* `PUT /{id}` → Update user
* `DELETE /{id}` → Delete user

### Logs - `/logs`

* `POST /` → Create new daily log
* `GET /` → Get all user logs
* `GET /{id}` → Log by ID
* `PUT /{id}` → Update log
* `DELETE /{id}` → Remove log

### Entries - `/logs/{log_id}/entries`

* `POST /` → Add food entry
* `GET /` → List entries
* `GET /{entry_id}` → Entry by ID
* `PUT /{entry_id}` → Update entry
* `DELETE /{entry_id}` → Remove entry

### Foods - `/foods`

* `GET /` → All food items
* `GET /{id}` → Food by ID
* `POST /` → Add food (admin only)
* `PUT /{id}` → Update food
* `DELETE /{id}` → Delete food
* `GET /search/?query=` → Search by name

### Admin - `/admin`

* `GET /stats` → Overall usage stats
* `GET /users-activity` → Recent activity

### Diagnostics

* `GET /health` → App health check

---

## 6. Authentication

* Uses OAuth2 with JWT
* Passwords hashed with bcrypt
* Protected routes use FastAPI's `Depends` to extract and verify users
* Access roles (admin/user) enforced in dependency layer

---

## 7. CRUD Architecture

All models use a reusable base class with:

```python
create(), update(), delete(), get_one(), get_many(), get_many_from_user()
```

This DRY structure helps maintain consistency across DB access patterns.

---

## 8. Testing

Tests are grouped into:

* `endpoint/` → Individual route tests
* `integration/` → End-to-end and serialization tests
* `unit/` → Authentication system and schema tests
* Uses fixtures and separate test DB

---

## 9. Running Locally

```bash
uvicorn backend.main:app --reload
```

* Swagger: `http://localhost:8000/docs`
* ReDoc: `http://localhost:8000/redoc`

---

## 10. License

MIT License — feel free to use, modify, and contribute.

---

## 11. Contact

For questions or contributions, contact [Max Kushnir](https://github.com/Max-Kushnir).
