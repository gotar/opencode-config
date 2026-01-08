"""
Comprehensive test suite for FastAPI example.

This example shows:
- pytest fixtures
- Async test configuration
- Mocking dependencies
- Parametrized tests
- Client testing
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch

# Import app and models
from main import app
from models import Item, ItemCreate, Status


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def sample_item():
    """Create sample item."""
    return Item(
        id=1,
        name="Test Item",
        description="A test item",
        price=99.99,
        status=Status.PUBLISHED,
        created_at="2024-01-01T00:00:00Z",
        updated_at="2024-01-01T00:00:00Z",
    )


# Tests
def test_root(client: TestClient) -> None:
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Welcome to Example API"
    assert data["version"] == "1.0.0"


def test_health_check(client: TestClient) -> None:
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_create_item(client: TestClient) -> None:
    """Test creating an item."""
    item_data = {
        "name": "New Item",
        "description": "A new item",
        "price": 49.99,
        "status": "draft",
    }

    response = client.post("/items", json=item_data)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "New Item"
    assert data["price"] == 49.99


def test_create_item_validation(client: TestClient) -> None:
    """Test validation on item creation."""
    # Invalid: empty name
    response = client.post(
        "/items",
        json={"name": "", "price": 10.0},
    )
    assert response.status_code == 422  # Validation error

    # Invalid: negative price
    response = client.post(
        "/items",
        json={"name": "Item", "price": -10.0},
    )
    assert response.status_code == 422


def test_get_item(client: TestClient, sample_item: Item) -> None:
    """Test getting an item by ID."""
    response = client.get("/items/1")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert data["name"] == sample_item.name


def test_get_item_not_found(client: TestClient) -> None:
    """Test getting non-existent item."""
    response = client.get("/items/999")
    assert response.status_code == 404


def test_list_items(client: TestClient) -> None:
    """Test listing items."""
    response = client.get("/items")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.parametrize("skip,limit", [(0, 10), (10, 20), (0, 50)])
def test_list_items_pagination(client: TestClient, skip: int, limit: int) -> None:
    """Test listing items with pagination."""
    response = client.get(f"/items?skip={skip}&limit={limit}")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_update_item(client: TestClient) -> None:
    """Test updating an item."""
    update_data = {
        "name": "Updated Item",
        "price": 149.99,
    }

    response = client.put("/items/1", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Item"
    assert data["price"] == 149.99


def test_delete_item(client: TestClient) -> None:
    """Test deleting an item."""
    response = client.delete("/items/1")
    assert response.status_code == 204


# Pydantic model tests
def test_item_create_model() -> None:
    """Test ItemCreate Pydantic model."""
    item = ItemCreate(
        name="Test Item",
        description="Test description",
        price=99.99,
        status=Status.PUBLISHED,
    )

    assert item.name == "Test Item"
    assert item.status == Status.PUBLISHED


def test_item_create_validation() -> None:
    """Test ItemCreate validation."""
    with pytest.raises(ValueError):
        ItemCreate(name="", price=10.0)  # Empty name

    with pytest.raises(ValueError):
        ItemCreate(name="Item", price=-10.0)  # Negative price


def test_item_update_model() -> None:
    """Test ItemUpdate Pydantic model."""
    # All fields optional
    update = ItemUpdate()
    assert update.name is None

    # Partial update
    update = ItemUpdate(name="New Name")
    assert update.name == "New Name"
    assert update.description is None


# Async tests (with pytest-asyncio)
@pytest.mark.asyncio
async def test_async_operation() -> None:
    """Test async operation."""
    import asyncio

    result = await asyncio.sleep(0.1, result="done")
    assert result == "done"


# Mock tests
def test_with_mocked_database(client: TestClient) -> None:
    """Test with mocked database dependency."""

    async def mock_get_db():
        """Mock database dependency."""
        mock_session = AsyncMock()
        yield mock_session

    # Replace dependency
    from main import get_db

    app.dependency_overrides[get_db] = mock_get_db

    try:
        response = client.get("/items")
        assert response.status_code == 200
    finally:
        app.dependency_overrides.clear()


# Run tests with: uv run pytest
# Run with coverage: uv run pytest --cov=examples --cov-report=html
