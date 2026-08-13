# Backend API Tests

Tests for the Mergington High School Activities API using pytest and FastAPI's TestClient.

## Running Tests

### Run all tests
```bash
pytest
```

### Run tests with verbose output
```bash
pytest -v
```

### Run tests with coverage report
```bash
pytest --cov=src tests/
```

### Run specific test file
```bash
pytest tests/test_endpoints.py
pytest tests/test_errors.py
```

### Run specific test class
```bash
pytest tests/test_endpoints.py::TestGetActivities
pytest tests/test_errors.py::TestSignUpErrors
```

### Run specific test
```bash
pytest tests/test_endpoints.py::TestGetActivities::test_get_activities_returns_all_activities
```

### Watch mode (requires pytest-watch)
```bash
pip install pytest-watch
ptw
```

## Test Structure

### `conftest.py`
Shared test configuration and fixtures:
- `reset_activities`: Fixture that resets the in-memory activities data before and after each test to ensure isolation
- `client`: TestClient instance for making HTTP requests to the API

### `test_endpoints.py`
Happy path tests for all API endpoints:
- **TestGetActivities**: GET /activities endpoint
  - Returns all 10 activities
  - Verifies correct data structure
  - Checks participant data accuracy
- **TestRootRedirect**: GET / endpoint
  - Verifies redirect to /static/index.html
- **TestSignUp**: POST /activities/{activity_name}/signup endpoint
  - Successful signup for new students
  - Participant count increases
  - Multiple students can sign up for same activity
- **TestUnregister**: DELETE /activities/{activity_name}/unregister endpoint
  - Successful unregistration
  - Participant count decreases
  - Multiple participants can unregister

### `test_errors.py`
Error handling and edge case tests:
- **TestSignUpErrors**: Signup failure scenarios
  - Non-existent activity (404)
  - Duplicate signup (400)
  - Empty email handling
  - URL encoding with special characters
- **TestUnregisterErrors**: Unregister failure scenarios
  - Non-existent activity (404)
  - Student not signed up (400)
  - Already unregistered student
  - Empty email handling
- **TestActivityDataIntegrity**: Data consistency tests
  - Signup/unregister reverses correctly
  - Participant counts are consistent
  - No duplicate participants
- **TestURLEncoding**: URL encoding edge cases
  - Activity names with spaces
  - Emails with special characters (+ signs)

## Test Coverage

Current test suite covers:
- All 4 API endpoints (GET /, GET /activities, POST /signup, DELETE /unregister)
- Happy path scenarios for each endpoint
- Error cases and validation failures
- Data isolation between tests
- URL encoding and special characters
- Data integrity across signup/unregister operations

Expected coverage: ~90% for API endpoints

## Dependencies

- `pytest` - Test runner
- `pytest-cov` - Coverage reporting
- `fastapi` - Web framework with TestClient
- `httpx` - HTTP client (included with FastAPI)

## Continuous Integration

To run tests in CI/CD pipeline:
```bash
pytest --cov=src --cov-report=html tests/
```

This generates an HTML coverage report in `htmlcov/index.html`.

## Debugging Tests

### Run with print statements
```bash
pytest -s tests/test_endpoints.py::TestGetActivities::test_get_activities_returns_all_activities
```

### Run with pdb debugger
```bash
pytest --pdb tests/test_endpoints.py::TestGetActivities::test_get_activities_returns_all_activities
```

### Run with traceback
```bash
pytest --tb=long tests/
```

## Notes

- Each test is isolated via the `reset_activities` fixture, ensuring data resets between tests
- Tests use FastAPI's TestClient which simulates HTTP requests without a running server
- The in-memory activities dictionary is deep-copied for each test, preserving the original structure
- Tests are organized by concern: happy paths in test_endpoints.py, errors in test_errors.py
