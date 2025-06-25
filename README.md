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