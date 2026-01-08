# FastAPI Example

A complete FastAPI example demonstrating modern Python best practices.

## Files

- **fastapi_app.py**: Main FastAPI application with routes, middleware, and logging
- **config.py**: Configuration management with Pydantic Settings
- **models.py**: Pydantic models for request/response validation
- **database.py**: Database connection and session management
- **test_example.py**: Comprehensive test suite

## Features

✅ **FastAPI** - Modern async web framework with auto documentation
✅ **Pydantic** - Type validation and settings management
✅ **Structured Logging** - JSON logs with context
✅ **Dependency Injection** - Database sessions and other dependencies
✅ **CORS Middleware** - Cross-origin resource sharing
✅ **Comprehensive Tests** - pytest with async support

## Quick Start

### Installation

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install fastapi uvicorn pydantic pydantic-settings sqlalchemy structlog asyncpg pytest pytest-asyncio httpx

# Or with uv
uv init fastapi-example
cd fastapi-example
uv add fastapi uvicorn pydantic pydantic-settings sqlalchemy structlog asyncpg pytest pytest-asyncio httpx
```

### Run Server

```bash
# Development server with auto-reload
uv run uvicorn fastapi_app:app --reload --host 0.0.0.0 --port 8000

# Or with python
python -m uvicorn fastapi_app:app --reload
```

### Access API

- **API Docs**: http://localhost:8000/docs (Swagger UI)
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## Endpoints

### Root
```bash
curl http://localhost:8000/
```

Response:
```json
{
  "message": "Welcome to Example API",
  "version": "1.0.0"
}
```

### Health Check
```bash
curl http://localhost:8000/health
```

### Create Item
```bash
curl -X POST http://localhost:8000/items \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Example Item",
    "description": "An example item",
    "price": 99.99,
    "status": "published"
  }'
```

### Get Item
```bash
curl http://localhost:8000/items/1
```

### List Items
```bash
curl "http://localhost:8000/items?skip=0&limit=10"
```

### Update Item
```bash
curl -X PUT http://localhost:8000/items/1 \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Updated Item",
    "price": 149.99
  }'
```

### Delete Item
```bash
curl -X DELETE http://localhost:8000/items/1
```

## Configuration

Create `.env` file:

```bash
DEBUG=true
HOST=0.0.0.0
PORT=8000
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/mydb
SECRET_KEY=your-secret-key-here
LOG_LEVEL=INFO
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
```

## Testing

### Run Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=examples --cov-report=html

# Run specific test
uv run pytest test_example.py::test_root

# Run with verbose output
uv run pytest -v

# Run async tests
uv run pytest -m asyncio
```

### Test Output

```bash
$ pytest -v
================================ test session starts =========================
collected 15 items

test_example.py::test_root PASSED                                   [  6%]
test_example.py::test_health_check PASSED                           [ 13%]
test_example.py::test_create_item PASSED                           [ 20%]
test_example.py::test_create_item_validation PASSED                  [ 26%]
test_example.py::test_get_item PASSED                              [ 33%]
test_example.py::test_get_item_not_found PASSED                     [ 40%]
test_example.py::test_list_items PASSED                            [ 46%]
test_example.py::test_list_items_pagination[0-10] PASSED           [ 53%]
test_example.py::test_list_items_pagination[10-20] PASSED          [ 60%]
test_example.py::test_list_items_pagination[0-50] PASSED           [ 66%]
test_example.py::test_update_item PASSED                            [ 73%]
test_example.py::test_delete_item PASSED                            [ 80%]
test_example.py::test_item_create_model PASSED                      [ 86%]
test_example.py::test_item_create_validation PASSED                 [ 93%]
test_example.py::test_async_operation PASSED                        [100%]

================================ 15 passed in 0.5s ==========================
```

## Best Practices Demonstrated

### 1. Type Hints
```python
async def get_item(
    item_id: int,
    db: AsyncSession = Depends(get_db),
) -> Item:
    """Get item by ID."""
    ...
```

### 2. Pydantic Validation
```python
class ItemCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    price: float = Field(..., gt=0)
    status: Status = Field(default=Status.DRAFT)
```

### 3. Dependency Injection
```python
@app.get("/items/{item_id}")
async def get_item(
    item_id: int,
    db: AsyncSession = Depends(get_db),
) -> Item:
    ...
```

### 4. Structured Logging
```python
logger.info("Creating item", name=item.name)
logger.warning("Item not found", item_id=item_id)
```

### 5. Error Handling
```python
raise HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Item not found",
)
```

### 6. Configuration Management
```python
class Settings(BaseSettings):
    database_url: PostgresDsn = Field(..., env="DATABASE_URL")
    secret_key: str = Field(..., min_length=32)
```

## Production Deployment

### Using uvicorn directly

```bash
uvicorn fastapi_app:app --host 0.0.0.0 --port 8000 --workers 4
```

### Using gunicorn

```bash
gunicorn fastapi_app:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000
```

### Using Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY . .
RUN pip install -r requirements.txt

CMD ["uvicorn", "fastapi_app:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Additional Resources

- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **Pydantic Docs**: https://docs.pydantic.dev/
- **SQLAlchemy**: https://docs.sqlalchemy.org/
- **pytest**: https://docs.pytest.org/
