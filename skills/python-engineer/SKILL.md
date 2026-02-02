# Python Engineer Skill

Comprehensive Python development guidance for modern, production-ready applications. Covers best practices, tooling, frameworks, and productivity patterns.

## Metadata

- **Name**: python-engineer
- **Description**: Expert Python development with modern best practices, type hints, async/await, testing, packaging, and framework selection guidance
- **License**: MIT

---

## Design Philosophy

### Purpose
To provide authoritative guidance for Python development that balances:
- **Code quality** (PEP 8, type safety, testing)
- **Developer productivity** (tooling, automation, modern patterns)
- **Performance** (async, profiling, optimization)
- **Maintainability** (clear structure, documentation, modularity)

### Tone
- **Modern**: Python 3.9+ features, contemporary tooling (uv, ruff, setuptools_scm)
- **Practical**: Real-world patterns over theoretical purity
- **Opinionated**: Clear defaults with justification for alternatives

### Constraints

**ALWAYS**:
- Use type hints for public APIs
- Follow PEP 8 (enforced by black/ruff)
- Write tests with pytest
- Use `uv` for new projects (10-100x faster than pip)
- Prefer `src` layout for packages
- Use `pyproject.toml` (PEP 621 standard)

**NEVER**:
- Suppress type errors with `# type: ignore` (fix the code)
- Use mutable default arguments (use `None` and set default)
- Ignore test coverage (aim for >80%)
- Hardcode secrets (use environment variables/Pydantic Settings)
- Mix `print()` with logging (use proper logging)

### Differentiation

| Aspect | This Skill | Others |
|--------|------------|--------|
| **Python Version** | 3.9+ (current best practices) | Legacy 2.7/3.6 support |
| **Dependency Management** | uv (fast, modern) | poetry/pip/venv (slower) |
| **Linting** | ruff (Python-written, 10-100x faster) | black+flake8 (separate tools) |
| **Testing** | pytest with modern plugins | unittest/legacy approaches |
| **Packaging** | PEP 621 pyproject.toml + setuptools_scm | setup.py/setup.cfg |
| **Type Checking** | mypy strict mode for libraries | Optional/relaxed |

---

## Python Best Practices

### Code Style & Formatting

**Primary Tools**:
- **ruff**: Linting and formatting (replaces black, flake8, isort)
  - 10-100x faster than alternatives
  - Compatible with black 99% of the time
  - Write in Rust for performance
- Configuration in `pyproject.toml`:

```toml
[tool.ruff]
line-length = 88
target-version = "py39"

[tool.ruff.lint]
select = ["E", "F", "I", "N", "W"]
ignore = ["E501"]  # Let black handle line length

[tool.ruff.format]
quote-style = "double"
indent-style = "space"
```

**Pre-commit hooks** (`.pre-commit-config.yaml`):

```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.0
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format
```

### Type Hints

**Always use type hints for**:
- Function parameters and return values
- Class attributes
- Public API surfaces
- Complex data structures

```python
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from collections.abc import Sequence

# Preferred: Use dataclasses for structured data
@dataclass
class User:
    id: int
    name: str
    email: str
    roles: Sequence[str]

# Function with comprehensive type hints
async def fetch_users(
    *,
    limit: Optional[int] = None,
    filters: Dict[str, Any] | None = None,
) -> List[User]:
    """Fetch users from database.

    Args:
        limit: Maximum number of users to return
        filters: Key-value filters for query

    Returns:
        List of User objects
    """
    filters = filters or {}
    # Implementation
    return []
```

**Mypy configuration** (`pyproject.toml`):

```toml
[tool.mypy]
python_version = "3.9"
strict = true  # Libraries: strict mode
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
```

For applications, use `warn_return_any = true` without full strict mode.

### Testing with pytest

**Project structure**:

```
myproject/
├── src/
│   └── myproject/
│       ├── __init__.py
│       ├── main.py
│       └── utils.py
├── tests/
│   ├── conftest.py
│   ├── test_main.py
│   └── test_utils.py
```

**Example test** (`tests/test_utils.py`):

```python
import pytest
from myproject.utils import calculate_sum

def test_calculate_sum_basic():
    assert calculate_sum([1, 2, 3]) == 6

@pytest.mark.parametrize("input,expected", [
    ([], 0),
    ([1], 1),
    ([1, 2, 3], 6),
])
def test_calculate_sum_various(input, expected):
    assert calculate_sum(input) == expected

@pytest.mark.asyncio
async def test_async_function():
    result = await async_operation()
    assert result is not None
```

**pytest configuration** (`pyproject.toml`):

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py", "*_test.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = [
    "--strict-markers",
    "--strict-config",
    "--cov=src/myproject",
    "--cov-report=term-missing",
    "--cov-report=html",
]
```

### Async/await Patterns

**When to use async**:
- I/O-bound operations (HTTP requests, database queries)
- Network operations (websockets, streams)
- Concurrent tasks without CPU bottlenecks

**Example patterns**:

```python
import asyncio
from typing import AsyncIterable

# Parallel async operations
async def fetch_multiple(urls: Sequence[str]) -> List[Response]:
    """Fetch multiple URLs concurrently."""
    async with httpx.AsyncClient() as client:
        tasks = [client.get(url) for url in urls]
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        return responses

# Async context manager
class DatabaseConnection:
    async def __aenter__(self):
        self.conn = await asyncpg.connect(...)
        return self.conn

    async def __aexit__(self, exc_type, exc, tb):
        await self.conn.close()

# Async generator
async def stream_results(query: str) -> AsyncIterable[Dict]:
    """Stream database results row by row."""
    async with DatabaseConnection() as conn:
        async for row in conn.cursor(query):
            yield dict(row)
```

**Avoid async for**:
- CPU-intensive operations (use multiprocessing)
- Simple synchronous code that doesn't benefit from concurrency

---

## Project Structure

### Modern `src` Layout (Recommended for Packages)

```
myproject/
├── pyproject.toml          # PEP 621 configuration
├── README.md
├── LICENSE
├── .gitignore
├── .pre-commit-config.yaml
├── src/
│   └── myproject/
│       ├── __init__.py
│       ├── main.py
│       └── utils.py
├── tests/
│   ├── conftest.py
│   ├── __init__.py
│   └── test_main.py
├── docs/
│   └── index.md
└── .github/
    └── workflows/
        └── ci.yml
```

**Why `src` layout**:
- Prevents import confusion during development
- Ensures tests import from installed package, not source tree
- Better packaging behavior with tools like `setuptools_scm`

### `pyproject.toml` (PEP 621 Standard)

**Complete example**:

```toml
[build-system]
requires = ["hatchling", "setuptools-scm"]
build-backend = "hatchling.build"

[project]
name = "myproject"
dynamic = ["version"]
description = "A modern Python project"
readme = "README.md"
requires-python = ">=3.9"
license = {text = "MIT"}
authors = [
    {name = "Author Name", email = "author@example.com"},
]

keywords = ["python", "example"]
classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
]

dependencies = [
    "httpx>=0.25.0",
    "pydantic>=2.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "pytest-cov>=4.0.0",
    "pytest-asyncio>=0.21.0",
    "mypy>=1.0.0",
    "ruff>=0.1.0",
    "pre-commit>=3.0.0",
]
docs = [
    "mkdocs>=1.5.0",
    "mkdocs-material>=9.0.0",
]

[project.scripts]
myproject-cli = "myproject.main:cli"

[project.urls]
Homepage = "https://github.com/user/myproject"
Documentation = "https://myproject.readthedocs.io"
Repository = "https://github.com/user/myproject"
Issues = "https://github.com/user/myproject/issues"

[tool.setuptools_scm]
write_to = "src/myproject/_version.py"

[tool.ruff]
line-length = 88
target-version = "py39"

[tool.ruff.lint]
select = ["E", "F", "I", "N", "W"]
ignore = ["E501"]

[tool.mypy]
python_version = "3.9"
strict = true
warn_return_any = true
warn_unused_configs = true

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = [
    "--strict-markers",
    "--cov=src/myproject",
    "--cov-report=term-missing",
]
```

### Dependency Management with `uv`

**Installation**:
```bash
# Using pip (one-time)
pip install uv

# Or using the official installer
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Commands**:
```bash
# Create new project
uv init myproject

# Add dependencies
uv add httpx pydantic

# Add dev dependencies
uv add --dev pytest pytest-cov mypy ruff

# Run commands in virtual environment
uv run pytest
uv run myproject-cli

# Sync dependencies (create/update venv)
uv sync

# Update dependencies
uv lock --upgrade
```

**Why `uv`**:
- Written in Rust (10-100x faster than pip)
- Drop-in replacement for pip/pip-tools
- Built-in dependency resolution (like poetry)
- Works with existing `requirements.txt`

---

## Framework Selection

### Web Development

| Framework | Use Case | Key Features |
|-----------|----------|--------------|
| **FastAPI** | APIs, microservices | Async, auto docs, Pydantic validation, fast |
| **Django** | Full-stack apps | ORM, admin, authentication, batteries included |
| **Flask** | Simple microservices | Minimal, flexible, easy to learn |

**Choose FastAPI when**:
- Building REST/GraphQL APIs
- Need async I/O performance
- Want automatic OpenAPI docs
- Rapid development with type safety

**Choose Django when**:
- Building full-stack web applications
- Need built-in admin interface
- Require robust authentication/permissions
- Want ORM and database migrations out of the box

**Choose Flask when**:
- Building simple microservices
- Need maximum flexibility
- Learning web frameworks

**FastAPI best practices** (`main.py`):

```python
from fastapi import FastAPI, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Optional

app = FastAPI(
    title="My API",
    description="API documentation",
    version="1.0.0",
)

# Pydantic models for request/response
class UserCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: str = Field(..., regex=r"^[^@]+@[^@]+\.[^@]+$")

class User(BaseModel):
    id: int
    name: str
    email: str

# Dependency injection
async def get_db():
    """Database session dependency."""
    async with async_session() as session:
        yield session

# Routes with proper status codes
@app.post("/users", response_model=User, status_code=status.HTTP_201_CREATED)
async def create_user(
    user: UserCreate,
    db: AsyncSession = Depends(get_db),
) -> User:
    """Create a new user."""
    # Implementation
    return user

@app.get("/users/{user_id}", response_model=User)
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
) -> User:
    """Get user by ID."""
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user

@app.get("/users", response_model=List[User])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
) -> List[User]:
    """List users with pagination."""
    return await db.execute(select(User).offset(skip).limit(limit))
```

### Database

**SQLAlchemy 2.0 with async support**:

```python
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker

# Async engine
DATABASE_URL = "postgresql+asyncpg://user:pass@localhost/db"
engine = create_async_engine(DATABASE_URL, echo=True)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)

# Async CRUD operations
async def create_user(user_data: dict) -> User:
    async with async_session() as session:
        user = User(**user_data)
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user

async def get_user(user_id: int) -> Optional[User]:
    async with async_session() as session:
        return await session.get(User, user_id)
```

**Alembic migrations**:

```bash
# Initialize migrations
alembic init alembic

# Create migration
alembic revision --autogenerate -m "Add users table"

# Apply migrations
alembic upgrade head
```

### Configuration Management

**Pydantic Settings** (`config.py`):

```python
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Application settings
    app_name: str = "My App"
    debug: bool = False

    # Database
    database_url: str = Field(..., env="DATABASE_URL")

    # Security
    secret_key: str = Field(..., env="SECRET_KEY")
    jwt_algorithm: str = "HS256"

    # External services
    api_key: Optional[str] = None

settings = Settings()
```

**Usage** (`.env` file):

```bash
DATABASE_URL=postgresql+asyncpg://user:pass@localhost/db
SECRET_KEY=your-secret-key-here
DEBUG=false
```

### Logging

**Structured logging with structlog** (`logging.py`):

```python
import structlog
import logging

def configure_logging(debug: bool = False) -> None:
    """Configure structured logging."""
    level = logging.DEBUG if debug else logging.INFO

    # Standard library logging
    logging.basicConfig(
        format="%(message)s",
        level=level,
    )

    # Structlog configuration
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.dev.set_exc_info,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer() if not debug else structlog.dev.ConsoleRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(level),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )

# Usage
logger = structlog.get_logger(__name__)
logger.info("User created", user_id=123, email="user@example.com")
```

---

## CLI Development

### Typer for Modern CLIs

**Example CLI** (`cli.py`):

```python
import typer
from typing import Optional

app = typer.Typer()

@app.command()
def hello(
    name: str = typer.Argument(..., help="Name to greet"),
    uppercase: bool = typer.Option(False, "--upper", "-u", help="Uppercase output"),
    count: int = typer.Option(1, "--count", "-c", help="Number of times to greet"),
) -> None:
    """Greet someone."""
    greeting = f"Hello, {name}!"
    if uppercase:
        greeting = greeting.upper()

    for _ in range(count):
        typer.echo(greeting)

if __name__ == "__main__":
    app()
```

**Usage**:
```bash
python cli.py World --upper --count 3
# Output: HELLO, WORLD!
#         HELLO, WORLD!
#         HELLO, WORLD!
```

### Entry Points

**Define in `pyproject.toml`**:

```toml
[project.scripts]
myproject-cli = "myproject.cli:app"
```

**After installation**:
```bash
myproject-cli World --upper
```

---

## Package Development & Distribution

### Publishing to PyPI

**Build with hatch/uv**:

```bash
# Install build tools
uv pip install build twine

# Build package
uv run build

# Check distribution
twine check dist/*

# Upload to PyPI
twine upload dist/*
```

**Versioning with `setuptools_scm`**:

```toml
[build-system]
requires = ["hatchling", "setuptools_scm"]
build-backend = "hatchling.build"

[tool.setuptools_scm]
write_to = "src/myproject/_version.py"
```

**Version automatically determined from**:
- Latest git tag (e.g., `v1.0.0`)
- Number of commits since tag
- Commit hash for dev versions

### CI/CD with GitHub Actions

**Complete workflow** (`.github/workflows/ci.yml`):

```yaml
name: CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.9", "3.10", "3.11", "3.12"]

    steps:
      - uses: actions/checkout@v4

      - name: Set up uv
        uses: astral-sh/setup-uv@v1
        with:
          version: "latest"

      - name: Set up Python ${{ matrix.python-version }}
        run: uv python install ${{ matrix.python-version }}

      - name: Install dependencies
        run: uv sync --dev

      - name: Run linters
        run: |
          uv run ruff check .
          uv run ruff format --check .

      - name: Run type checks
        run: uv run mypy src

      - name: Run tests
        run: uv run pytest --cov=src/myproject --cov-report=xml

      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v4

  build:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, macos-latest, windows-latest]
        python-version: ["3.9", "3.10", "3.11", "3.12"]

    steps:
      - uses: actions/checkout@v4

      - name: Build wheels
        uses: pypa/cibuildwheel@v2
        env:
          CIBW_BUILD: cp39-* cp310-* cp311-* cp312-*

      - uses: actions/upload-artifact@v4
        with:
          name: wheels
          path: wheelhouse/*.whl
```

---

## Documentation

### Docstring Conventions

**Google style** (recommended):

```python
def calculate_discount(
    price: float,
    discount_rate: float,
    quantity: int = 1,
) -> float:
    """Calculate the discounted price for an item.

    Args:
        price: The original price of the item.
        discount_rate: The discount rate as a decimal (e.g., 0.2 for 20%).
        quantity: The number of items. Defaults to 1.

    Returns:
        The discounted total price.

    Raises:
        ValueError: If price is negative or discount_rate is not between 0 and 1.

    Examples:
        >>> calculate_discount(100.0, 0.2, 2)
        160.0
    """
    if price < 0:
        raise ValueError("Price must be non-negative")
    if not 0 <= discount_rate <= 1:
        raise ValueError("Discount rate must be between 0 and 1")

    return price * (1 - discount_rate) * quantity
```

### MkDocs Documentation

**Configuration** (`mkdocs.yml`):

```yaml
site_name: My Project
site_description: Modern Python project documentation
site_url: https://myproject.readthedocs.io

theme:
  name: material
  palette:
    - scheme: default
      primary: indigo
      accent: indigo
      toggle:
        icon: material/brightness-7
        name: Switch to dark mode
    - scheme: slate
      primary: indigo
      accent: indigo
      toggle:
        icon: material/brightness-4
        name: Switch to light mode

plugins:
  - search
  - mkdocstrings:
      handlers:
        python:
          options:
            show_source: true
            show_root_heading: true
            show_root_full_path: false

markdown_extensions:
  - pymdownx.highlight:
      anchor_linenums: true
  - pymdownx.superfences

nav:
  - Home: index.md
  - Installation: installation.md
  - Usage: usage.md
  - API Reference: api/
```

---

## Anti-Patterns & Common Mistakes

### Code Quality Anti-Patterns

**❌ Bad**: Mutable default arguments
```python
def process_items(items: List = []):  # Mutates across calls!
    items.append("processed")
    return items
```

**✅ Good**: Use `None` as default
```python
from typing import Optional, List

def process_items(items: Optional[List] = None) -> List:
    if items is None:
        items = []
    items.append("processed")
    return items
```

**❌ Bad**: Empty except blocks
```python
try:
    risky_operation()
except:  # Swallows ALL errors including KeyboardInterrupt!
    pass
```

**✅ Good**: Specific exception handling
```python
try:
    risky_operation()
except ValueError as e:
    logger.error("Invalid value", error=str(e))
    raise
except Exception as e:
    logger.exception("Unexpected error")
    raise
```

**❌ Bad**: Using `print()` for logging
```python
def process_data(data):
    print(f"Processing: {data}")  # No timestamps, no levels, can't disable
    # ... process
    print(f"Done: {data}")
```

**✅ Good**: Proper logging
```python
import logging

logger = logging.getLogger(__name__)

def process_data(data):
    logger.info("Processing data", data=data)
    # ... process
    logger.info("Processing complete", data=data)
```

**❌ Bad**: Suppressing type errors
```python
def process(item: Any) -> str:  # Avoid Any!
    return item.do_something()  # mypy error: Item has no attribute
```

**✅ Good**: Fix type errors or use proper typing
```python
from typing import Protocol

class Processable(Protocol):
    def do_something(self) -> str: ...

def process(item: Processable) -> str:
    return item.do_something()  # Type-safe!
```

### Performance Anti-Patterns

**❌ Bad**: String concatenation in loops
```python
def build_string(items: List[str]) -> str:
    result = ""
    for item in items:  # O(n²) - creates new string each iteration
        result += item
    return result
```

**✅ Good**: Use `join()`
```python
def build_string(items: List[str]) -> str:
    return "".join(items)  # O(n)
```

**❌ Bad**: Synchronous HTTP calls in async function
```python
async def fetch_data(urls: List[str]) -> List[Dict]:
    results = []
    for url in urls:
        # Blocks the event loop!
        response = requests.get(url)
        results.append(response.json())
    return results
```

**✅ Good**: Async HTTP client
```python
import httpx

async def fetch_data(urls: List[str]) -> List[Dict]:
    async with httpx.AsyncClient() as client:
        tasks = [client.get(url) for url in urls]
        responses = await asyncio.gather(*tasks)
        return [r.json() for r in responses]
```

### Security Anti-Patterns

**❌ Bad**: Hardcoded secrets
```python
API_KEY = "sk-1234567890abcdef"  # Never commit secrets!

def fetch_data():
    requests.get("https://api.example.com/data", params={"key": API_KEY})
```

**✅ Good**: Environment variables + Pydantic Settings
```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    api_key: str  # Loaded from API_KEY env var

    class Config:
        env_file = ".env"

settings = Settings()

def fetch_data():
    requests.get(
        "https://api.example.com/data",
        params={"key": settings.api_key},
    )
```

**❌ Bad**: SQL injection with f-strings
```python
def get_user(username: str):
    cursor.execute(f"SELECT * FROM users WHERE name = '{username}'")  # Injection!
```

**✅ Good**: Parameterized queries
```python
def get_user(username: str):
    cursor.execute("SELECT * FROM users WHERE name = %s", (username,))
```

---

## Reference Resources

### Official Documentation
- **Python Language**: https://docs.python.org/3/
- **PEP 8 Style Guide**: https://peps.python.org/pep-0008/
- **PEP 621 pyproject.toml**: https://peps.python.org/pep-0621/
- **Type Hints**: https://docs.python.org/3/library/typing.html

### Modern Tooling
- **uv**: https://github.com/astral-sh/uv (Fast Python package manager)
- **ruff**: https://docs.astral.sh/ruff/ (Fast linter/formatter)
- **pytest**: https://docs.pytest.org/
- **mypy**: https://mypy.readthedocs.io/
- **FastAPI**: https://fastapi.tiangolo.com/
- **SQLAlchemy**: https://docs.sqlalchemy.org/en/20/

### Best Practices
- **The Hitchhiker's Guide to Python**: https://docs.python-guide.org/
- **Real Python**: https://realpython.com/
- **Effective Python**: https://effectivepython.com/
- **Python Packaging Authority**: https://www.pypa.io/

### Example Projects
- **FastAPI**: https://github.com/tiangolo/fastapi
- **pydantic**: https://github.com/pydantic/pydantic
- **SQLAlchemy**: https://github.com/sqlalchemy/sqlalchemy
- **Typer**: https://github.com/fastapi/typer

---

## Quick Start Example

### Project Setup

```bash
# 1. Initialize project with uv
uv init myproject
cd myproject

# 2. Add dependencies
uv add httpx pydantic pydantic-settings

# 3. Add dev dependencies
uv add --dev pytest pytest-cov pytest-asyncio mypy ruff pre-commit

# 4. Create project structure
mkdir -p src/myproject tests

# 5. Set up pre-commit hooks
uv run pre-commit install
```

### Main Application (`src/myproject/main.py`)

```python
from fastapi import FastAPI
from pydantic import BaseModel
import structlog

from config import settings

app = FastAPI(title="My API", version="1.0.0")
logger = structlog.get_logger(__name__)

class Item(BaseModel):
    name: str
    price: float

@app.get("/")
async def root() -> dict:
    """Root endpoint."""
    logger.info("Root endpoint called")
    return {"message": "Hello World"}

@app.post("/items", status_code=201)
async def create_item(item: Item) -> Item:
    """Create a new item."""
    logger.info("Creating item", item=item)
    return item
```

### Configuration (`src/myproject/config.py`)

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "My App"
    debug: bool = False

    class Config:
        env_file = ".env"

settings = Settings()
```

### Test (`tests/test_main.py`)

```python
import pytest
from fastapi.testclient import TestClient

from myproject.main import app

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World"}

def test_create_item():
    item = {"name": "Test Item", "price": 9.99}
    response = client.post("/items", json=item)
    assert response.status_code == 201
    assert response.json() == item
```

### Run Project

```bash
# Run tests
uv run pytest

# Run API
uv run uvicorn myproject.main:app --reload

# Type check
uv run mypy src

# Format/lint
uv run ruff check --fix .
uv run ruff format .
```

---

## Decision Trees

### "Which Python Framework Should I Use?"

```
What are you building?
├─ REST API / Microservices
│  └─ Performance critical?
│     ├─ Yes (10k+ req/s)
│     │  └─ FastAPI + async
│     │     • Auto-generated OpenAPI docs
│     │     • Pydantic validation
│     │     • Async I/O for high throughput
│     │
│     └─ No (standard load)
│        └─ FastAPI (still) or Flask
│           • FastAPI: modern, type-safe, auto-docs
│           • Flask: simpler, more flexible
│
├─ Full-stack Web Application
│  └─ Need admin interface?
│     ├─ Yes
│     │  └─ Django
│     │     • Built-in admin
│     │     • ORM with migrations
│     │     • Authentication/permissions
│     │
│     └─ No
│        └─ FastAPI + Jinja2
│           • API-first with server-side rendering
│           • Hotwire/Turbo compatibility
│
├─ Simple Script / CLI
│  └─ Typer (recommended)
│     • Type hints for CLI args
│     • Auto-generated help
│     • Shell completion
│
└─ Data Science / ML
   └─ FastAPI for serving models
      • Async prediction endpoints
      • Pydantic for request validation
      • Easy integration with ML libraries
```

### "Sync vs Async - Which Should I Use?"

```
What does your code do?
├─ I/O Operations (network, disk, database)
│  └─ Use async/await
│     • HTTP requests (httpx.AsyncClient)
│     • Database queries (asyncpg, async SQLAlchemy)
│     • File I/O (aiofiles for heavy operations)
│     • Multiple concurrent operations
│     • WebSocket connections
│
├─ CPU-Intensive Work (calculations, data processing)
│  └─ Use sync with multiprocessing
│     • Machine learning inference
│     • Image/video processing
│     • Heavy data transformations
│     • Use ProcessPoolExecutor, not threads
│
└─ Mixed Workload
   └─ Async for I/O + ProcessPool for CPU
      • FastAPI route (async)
      • Offload CPU work to process pool
      • Example: async endpoint → process image
```

### "How Should I Structure My Project?"

```
Project type?
├─ Single script/tool
│  └─ Single file with main()
│     • Use typer for CLI
│     • Add if __name__ == "__main__"
│     • Example: mytool.py
│
├─ Library / Package (published to PyPI)
│  └─ src/ layout
│     • src/mypackage/ (code)
│     • tests/ (pytest)
│     • docs/ (mkdocs)
│     • pyproject.toml (PEP 621)
│     • Why: prevents import confusion
│
├─ Application / Service
│  └─ Flat or src/ layout
│     • app/ or src/app/ (application code)
│     • tests/ (pytest + coverage)
│     • config/ (settings per environment)
│     • Dockerfile + docker-compose.yml
│
└─ Monorepo (multiple packages)
   └─ Separate packages with shared config
      • package_a/, package_b/
      • Each: pyproject.toml, src/, tests/
      • Root: shared CI config, Makefile
```

### "Which Database Should I Use?"

```
Data requirements?
├─ Relational data (relations, transactions)
│  └─ PostgreSQL (recommended)
│     • Async support: asyncpg
│     • ORM: SQLAlchemy 2.0 (async)
│     • Migrations: Alembic
│
├─ Document / JSON data
│  └─ MongoDB
│     • Motor for async driver
│     • Pydantic for schema validation
│     • Good for unstructured data
│
├─ Key-Value / Cache
│  └─ Redis
│     • redis-py (async support)
│     • Caching, sessions, rate limiting
│
├─ Simple / Embedded
│  └─ SQLite
│     • Good for testing, small apps
│     • aiosqlite for async
│     • Limited concurrency (not for high traffic)
│
└─ Time-series data
   └─ TimescaleDB (PostgreSQL extension)
      • Time-series optimizations
      • SQL interface
```

### "Which Testing Approach?"

```
What to test?
├─ Unit tests (functions, classes)
│  └─ pytest with fixtures
│     • Mock external dependencies
│     • Test edge cases, errors
│     • Parametrize for multiple cases
│
├─ Integration tests (database, APIs)
│  └─ pytest + testcontainers
│     • Spin up real services in containers
│     • Test with actual database
│     • Slower but more realistic
│
├─ API endpoints
│  └─ FastAPI TestClient
│     • In-memory testing
│     • Fast, no server needed
│     • Test request/response schemas
│
└─ E2E / Browser testing
   └─ Playwright or Selenium
      • Real browser automation
      • Prefer agent-browser skill for this
      • Test complete user flows
```

### "Deployment Strategy Decision"

```
Where to deploy?
├─ Cloud Platform
│  ├─ AWS
│  │  └─ ECS Fargate (containers)
│  │     • FastAPI in Docker
│  │     • RDS for PostgreSQL
│  │     • ALB for load balancing
│  │
│  ├─ Google Cloud
│  │  └─ Cloud Run (serverless containers)
│  │     • Auto-scaling
│  │     • Pay per request
│  │     • Perfect for FastAPI
│  │
│  └─ Azure
│     └─ Container Apps
│        • Similar to Cloud Run
│        • Good integration with Azure services
│
├─ VPS / Bare Metal
│  └─ Docker + Kamal (for Rails projects)
│     • Or Docker Compose for simpler setups
│     • Traefik or Nginx for reverse proxy
│     • Let's Encrypt for SSL
│
└─ Serverless
   └─ AWS Lambda + API Gateway
      • Zappa or Mangum for FastAPI
      • Good for sporadic traffic
      • Cold start latency consideration
```

---

## Self-Learning & Improvement

### Trace Capture Template

After completing a Python development task, document:

```markdown
# Trace: python-engineer_[timestamp]
Skill: python-engineer
Task: [brief description]
Status: [success/partial/failure]

## Architecture Decisions
- Framework chosen: [FastAPI/Django/Flask/Typer]
- Database: [PostgreSQL/SQLite/MongoDB]
- Async/Sync: [choice and rationale]
- Testing approach: [unit/integration/e2e]

## Tools Used
- [tool 1]
- [tool 2]

## Challenges Encountered
- [Issue 1]
- [Issue 2]

## Solutions Applied
- [Solution 1]
- [Solution 2]

## Performance Metrics
- Response time: [X ms]
- Test coverage: [X%]
- LOC: [X lines]
- Dependencies: [X packages]

## Key Learnings
- [What worked well]
- [What to do differently]
- [New pattern discovered]
```

Save to: `.tmp/learning/traces/python-engineer_[timestamp].md`

### Pattern Recognition

After 5+ traces, analyze for:
- **Framework patterns**: Which framework worked best for which use case?
- **Performance patterns**: Common bottlenecks and optimizations
- **Testing patterns**: What caught the most bugs?
- **Tooling patterns**: Which tools saved the most time?

Extract insights to: `.tmp/learning/insights/python-engineer.md`

### Common Patterns to Track

**Success Patterns:**
- FastAPI + asyncpg + Pydantic for high-performance APIs
- SQLAlchemy 2.0 with explicit async session management
- Pydantic Settings for configuration (type-safe, validated)
- pytest with fixtures and parametrize for comprehensive testing
- ruff for linting (speed, comprehensive rules)
- uv for dependency management (speed, lock files)

**Failure Patterns:**
- Using requests in async functions (blocks event loop)
- Mutable default arguments in functions
- Not handling database session cleanup in async context
- Mixing sync and async code without care
- Skipping type hints on public APIs
- Using print() instead of structured logging

**Efficiency Opportunities:**
- Code generation from Pydantic models (datamodel-code-generator)
- Automated API testing with schemathesis
- Property-based testing with hypothesis
- Caching with functools.lru_cache or cachetools

### Skill Evolution

If patterns emerge:
1. Update this SKILL.md with new learnings
2. Add new decision trees based on experience
3. Expand examples with real-world scenarios
4. Document common pitfalls with solutions
5. Add new framework/tool patterns as ecosystem evolves

---

## Integration with Other Skills

This skill provides comprehensive Python development guidance and can be integrated with other skills in the OpenCode ecosystem:

- **gtk-ui-ux-engineer**: Use Python for backend APIs that serve GTK applications
- **frontend-ui-ux-engineer**: Create Python-based REST APIs for frontend consumption
- **document-writer**: Generate API documentation from Python docstrings
- **rails-basecamp-engineer**: Apply Python patterns for microservices alongside Rails monoliths

The skill is designed to be invoked automatically when:
- Working with `.py` files
- Managing `pyproject.toml` or `requirements.txt`
- Running Python-related commands (`pytest`, `uv`, `ruff`)
- Setting up Python development environments

---

## When to Use This Skill

**Use this skill when**:
- Creating new Python projects or modules
- Setting up Python development environments
- Writing Python code with type hints and async patterns
- Choosing frameworks (FastAPI, Django, Flask)
- Packaging and distributing Python libraries
- Setting up testing, linting, and CI/CD
- Implementing configuration, logging, and error handling

**Do NOT use this skill for**:
- JavaScript/TypeScript development (use frontend-ui-ux-engineer)
- GTK UI development (use gtk-ui-ux-engineer)
- Ruby/Rails development (use rails-basecamp-engineer)
- Generic system administration (use appropriate domain skills)

---

## Skill Compatibility

**Minimum Python Version**: 3.9
**Recommended Python Version**: 3.11+ (for latest features and performance)
**Compatible Tools**: uv, ruff, pytest, mypy, FastAPI, Django 5+, SQLAlchemy 2.0+
