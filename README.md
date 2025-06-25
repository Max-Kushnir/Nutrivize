# Nutrition Tracker API Test Suite

This test suite provides comprehensive testing for the Nutrition Tracker API endpoints. The tests verify the behavior of all API routes, ensuring that authentication, authorization, and data operations work as expected.

## Test Structure

The test suite is organized by feature area:

1. **Authentication Tests** (`test_auth_routes.py`)
   - User registration
   - Login/logout
   - Token refresh
   - Current user retrieval

2. **User Management Tests** (`test_user_routes.py`)
   - User listing (admin)
   - User details retrieval
   - User updates
   - User deletion

3. **Daily Log Tests** (`test_daily_log_routes.py`)
   - Log creation
   - Log listing
   - Log updates
   - Log deletion

4. **Food Management Tests** (`test_food_routes.py`)
   - Food listing
   - Food search
   - Food creation (admin)
   - Food updates (admin)
   - Food deletion (admin)

5. **Food Entry Tests** (`test_food_entry_routes.py`)
   - Adding food to logs
   - Entry listing
   - Entry updates
   - Entry deletion

6. **Admin Tests** (`test_admin_routes.py`)
   - System stats
   - User activity monitoring
   - Database reset functionality

## Running the Tests

The tests use pytest and are designed to run against a PostgreSQL test database. To run the tests:

```bash
# Run all tests
pytest

# Run tests for a specific module
pytest test_auth_routes.py

# Run tests with verbose output
pytest -v

# Run tests with coverage report
pytest --cov=backend
```

## Test Database

The tests use a separate test database defined in your settings:

```
postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_TEST_DB}
```

Each test function gets a fresh database session, and tables are recreated for each test to ensure isolation.

## Test Fixtures

The test suite uses several fixtures to set up test data:

- `engine`: SQLAlchemy engine connected to the test database
- `tables`: Creates all tables before tests and drops them after
- `db_session`: Provides a database session for each test
- `client`: FastAPI test client
- `test_user`: A regular user account for testing
- `test_admin`: An admin user account for testing
- `user_token` / `admin_token`: JWT tokens for authentication
- `authorized_client`: Client with regular user authentication
- `admin_client`: Client with admin user authentication
- `test_foods`: Sample food items
- `test_daily_log`: A sample daily log
- `test_food_entries`: Sample food entries

## Adding New Tests

When adding new API functionality, follow these guidelines for creating tests:

1. Group related tests in the appropriate test file
2. Test both successful and error cases
3. Test authorization requirements
4. Verify database changes when applicable
5. Include tests for edge cases

## Authentication Testing Approach

The authentication tests verify:

1. User registration validation
2. Login with username and email
3. Token generation and verification
4. Authorization for protected routes
5. Token refresh functionality

## Data Validation Testing

The tests verify proper data validation by:

1. Testing invalid inputs
2. Verifying unique constraint handling
3. Testing cross-entity relationships
4. Verifying that operations only affect the user's own data
=======
# Nutrition Logger - Full Documentation

## 1. Overview

Nutrition Logger is a FastAPI-based backend application for tracking users' daily food consumption, logging nutritional intake, and providing admin-level analytics. It supports user authentication and role-based access control with a clean, modular architecture.

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
