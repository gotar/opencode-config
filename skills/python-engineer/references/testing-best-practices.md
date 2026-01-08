# Python Testing Best Practices

Comprehensive guide to testing Python applications with pytest, covering unit tests, integration tests, fixtures, mocking, and coverage.

## Table of Contents

1. [Project Structure for Tests](#project-structure-for-tests)
2. [Basic pytest Usage](#basic-pytest-usage)
3. [Fixtures](#fixtures)
4. [Parametrized Tests](#parametrized-tests)
5. [Mocking and Patching](#mocking-and-patching)
6. [Testing Async Code](#testing-async-code)
7. [Testing HTTP Clients](#testing-http-clients)
8. [Coverage Reporting](#coverage-reporting)
9. [CI/CD Integration](#cicd-integration)

---

## Project Structure for Tests

### Recommended Layout

```
myproject/
├── pyproject.toml
├── src/
│   └── myproject/
│       ├── __init__.py
│       ├── main.py
│       └── utils.py
├── tests/
│   ├── conftest.py          # Shared fixtures
│   ├── __init__.py
│   ├── test_main.py
│   ├── test_utils.py
│   └── integration/
│       ├── __init__.py
│       └── test_api.py
```

**Why this layout**:
- `tests/` at root level (no name collision)
- `conftest.py` for shared fixtures
- Subdirectories for integration/e2e tests
- `src/` layout ensures tests import from installed package

---

## Basic pytest Usage

### Simple Tests

```python
import pytest
from myproject.utils import calculate_sum, greet

def test_calculate_sum_basic():
    """Test basic sum calculation."""
    assert calculate_sum([1, 2, 3]) == 6

def test_calculate_sum_empty():
    """Test sum of empty list."""
    assert calculate_sum([]) == 0

def test_calculate_sum_negative():
    """Test sum with negative numbers."""
    assert calculate_sum([-1, 1, -2, 2]) == 0

def test_greet():
    """Test greeting function."""
    assert greet("Alice") == "Hello, Alice!"
```

### Assertions with Context

```python
def test_with_exception():
    """Test exception handling."""
    with pytest.raises(ValueError) as exc_info:
        raise ValueError("Invalid value")

    assert str(exc_info.value) == "Invalid value"

def test_with_warning():
    """Test warning."""
    with pytest.warns(UserWarning) as record:
        import warnings
        warnings.warn("Deprecated feature", UserWarning)

    assert len(record) == 1
    assert "Deprecated" in str(record[0].message)
```

### Test Markers

```python
import pytest

@pytest.mark.slow
def test_slow_operation():
    """Mark slow tests."""
    import time
    time.sleep(2)
    assert True

@pytest.mark.integration
def test_database():
    """Mark integration tests."""
    # Database test
    assert True

@pytest.mark.unit
def test_calculate():
    """Mark unit tests."""
    assert 1 + 1 == 2
```

Run specific markers:
```bash
# Run only unit tests
pytest -m unit

# Skip slow tests
pytest -m "not slow"

# Run only integration tests
pytest -m integration
```

---

## Fixtures

### Basic Fixtures

```python
# tests/conftest.py
import pytest
from myproject.main import create_app

@pytest.fixture
def app():
    """Create test app instance."""
    app = create_app()
    app.config["TESTING"] = True
    yield app

@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()
```

### Fixture Scopes

```python
@pytest.fixture(scope="function")
def db_session():
    """Create fresh database session for each test."""
    session = create_session()
    yield session
    session.rollback()
    session.close()

@pytest.fixture(scope="module")
def redis_client():
    """Create redis client for entire module."""
    client = redis.Redis()
    yield client
    client.flushdb()

@pytest.fixture(scope="session")
def test_data():
    """Load test data once per session."""
    return load_fixture_data("test_data.json")
```

### Dependent Fixtures

```python
@pytest.fixture
def user_data():
    """Create user data."""
    return {
        "name": "Alice",
        "email": "alice@example.com",
        "age": 30,
    }

@pytest.fixture
def user(client, user_data):
    """Create user in database."""
    response = client.post("/users", json=user_data)
    return response.json()

def test_get_user(client, user):
    """Test getting user."""
    response = client.get(f"/users/{user['id']}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == user["name"]
```

### Autouse Fixtures

```python
@pytest.fixture(autouse=True)
def setup_logging():
    """Setup logging for all tests."""
    import logging
    logging.basicConfig(level=logging.DEBUG)
    yield
    # Cleanup after all tests
```

---

## Parametrized Tests

### Parametrize with List

```python
@pytest.mark.parametrize("input,expected", [
    ([1, 2, 3], 6),
    ([], 0),
    ([1], 1),
    ([-1, 1], 0),
])
def test_calculate_sum_various(input, expected):
    """Test sum with various inputs."""
    assert calculate_sum(input) == expected
```

### Parametrize with Multiple Values

```python
@pytest.mark.parametrize("x,y,expected", [
    (1, 2, 3),
    (0, 0, 0),
    (-1, 1, 0),
    (100, 200, 300),
])
def test_add(x, y, expected):
    """Test addition."""
    assert x + y == expected
```

### Parametrize with Exception Cases

```python
@pytest.mark.parametrize("value,exception_type", [
    (None, TypeError),
    ("abc", ValueError),
    (-1, ValueError),
])
def test_validate_input(value, exception_type):
    """Test input validation."""
    with pytest.raises(exception_type):
        validate_input(value)
```

---

## Mocking and Patching

### Using unittest.mock

```python
from unittest.mock import Mock, patch, MagicMock

def test_external_api_call():
    """Test API call with mock."""
    # Create mock
    mock_response = Mock()
    mock_response.json.return_value = {"status": "success"}

    # Patch httpx.AsyncClient
    with patch("httpx.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__.return_value.get.return_value = mock_response

        # Call function
        result = fetch_data("https://api.example.com")

        # Assertions
        assert result == {"status": "success"}
        mock_client.assert_called_once()
```

### Mocking Database

```python
def test_user_creation():
    """Test user creation with mock DB."""
    # Mock database session
    mock_session = MagicMock()

    with patch("myproject.main.get_session") as mock_get_session:
        mock_get_session.return_value.__enter__.return_value = mock_session

        # Create user
        user = create_user("Alice", "alice@example.com")

        # Assertions
        assert user.name == "Alice"
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()
```

### Mocking Return Values

```python
def test_with_side_effect():
    """Test mock with side effect."""
    mock_func = Mock()

    # Set return value
    mock_func.return_value = "result"

    # Set side effect (multiple calls)
    mock_func.side_effect = ["first", "second", "third"]

    assert mock_func() == "first"
    assert mock_func() == "second"
    assert mock_func() == "third"
```

### Mocking Async Functions

```python
import pytest
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
async def test_async_function():
    """Test async function with mock."""
    async_mock = AsyncMock()
    async_mock.return_value = {"data": "result"}

    with patch("myproject.main.fetch_data", async_mock):
        result = await process_data("https://api.example.com")
        assert result == {"data": "result"}
```

---

## Testing Async Code

### pytest-asyncio Setup

Install:
```bash
uv add --dev pytest-asyncio
```

Configuration (`pyproject.toml`):
```toml
[tool.pytest.ini_options]
asyncio_mode = "auto"
```

### Async Tests

```python
import pytest

@pytest.mark.asyncio
async def test_async_function():
    """Test async function."""
    result = await async_operation()
    assert result is not None

@pytest.mark.asyncio
async def test_async_with_fixture(async_client):
    """Test async with fixture."""
    response = await async_client.get("/api/users")
    assert response.status_code == 200
```

### Async Fixtures

```python
@pytest.fixture
async def async_db_session():
    """Create async database session."""
    from myproject.database import async_session
    async with async_session() as session:
        yield session

@pytest.mark.asyncio
async def test_with_async_session(async_db_session):
    """Test with async session."""
    user = User(name="Alice")
    async_db_session.add(user)
    await async_db_session.commit()
    assert user.id is not None
```

---

## Testing HTTP Clients

### Using httpx TestClient

```python
from fastapi import FastAPI
from httpx import AsyncClient

app = FastAPI()

@app.get("/users/{user_id}")
async def get_user(user_id: int):
    return {"id": user_id, "name": "Alice"}

@pytest.mark.asyncio
async def test_get_user():
    """Test API endpoint."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/users/1")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 1
```

### Mocking HTTP Responses

```python
import pytest
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
async def test_external_api():
    """Test external API with mock."""
    mock_response = AsyncMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"result": "success"}

    with patch("httpx.AsyncClient.get", return_value=mock_response):
        result = await fetch_external_data()
        assert result == {"result": "success"}
```

---

## Coverage Reporting

### Running Coverage

```bash
# Run tests with coverage
pytest --cov=src/myproject

# Generate HTML report
pytest --cov=src/myproject --cov-report=html

# Report missing lines
pytest --cov=src/myproject --cov-report=term-missing

# Fail if coverage below threshold
pytest --cov=src/myproject --cov-fail-under=80
```

### Configuration (`pyproject.toml`)

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
addopts = [
    "--strict-markers",
    "--cov=src/myproject",
    "--cov-report=term-missing",
    "--cov-report=html",
    "--cov-fail-under=80",
]

[tool.coverage.run]
source = ["src"]
omit = ["*/tests/*", "*/venv/*", "*/__pycache__/*"]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise AssertionError",
    "raise NotImplementedError",
    "if __name__ == .__main__.:",
    "if TYPE_CHECKING:",
]
```

---

## CI/CD Integration

### GitHub Actions

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.9", "3.10", "3.11", "3.12"]

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}

      - name: Install uv
        run: pip install uv

      - name: Install dependencies
        run: uv sync --dev

      - name: Run linting
        run: |
          uv run ruff check .
          uv run ruff format --check .

      - name: Run type checking
        run: uv run mypy src

      - name: Run tests
        run: uv run pytest --cov=src/myproject --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v4
        with:
          file: ./coverage.xml
          flags: python-${{ matrix.python-version }}
```

---

## Best Practices

1. **Use descriptive test names**: `test_calculate_sum_with_empty_list`
2. **One assertion per test**: Tests should be simple and focused
3. **Arrange-Act-Assert pattern**: Clear test structure
4. **Use fixtures**: Share setup code across tests
5. **Mock external dependencies**: Don't test external APIs
6. **Test edge cases**: Empty lists, None values, negative numbers
7. **Aim for >80% coverage**: Higher is better for critical code
8. **Run tests in CI**: Catch regressions early
