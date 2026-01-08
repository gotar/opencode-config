# Python Type Hints Best Practices

Complete guide to type hints in Python, covering basic types, generics, protocols, and advanced patterns.

## Table of Contents

1. [Basic Types](#basic-types)
2. [Generics and Collections](#generics-and-collections)
3. [Optional and Union](#optional-and-union)
4. [Type Aliases and NewType](#type-aliases-and-newtype)
5. [Protocol and Structural Typing](#protocol-and-structural-typing)
6. [Overloaded Functions](#overloaded-functions)
7. [Async Type Hints](#async-type-hints)
8. [Pydantic Integration](#pydantic-integration)

---

## Basic Types

### Primitives

```python
from typing import Literal, Final

# Primitive types
name: str = "Alice"
age: int = 30
height: float = 5.9
is_active: bool = True
data: bytes = b"binary data"

# Literals (for specific values)
status: Literal["pending", "active", "completed"] = "pending"
color: Literal["red", "green", "blue"] = "red"

# Final (immutable values)
API_KEY: Final[str] = "fixed-key"
MAX_RETRIES: Final[int] = 3
```

### None and Optional

```python
from typing import Optional

# None is a valid type
def returns_none() -> None:
    """Function that returns nothing."""
    return

# Optional = T | None
def get_user(user_id: int) -> Optional[dict]:
    """Returns user or None if not found."""
    # Implementation
    if user_id == 0:
        return None
    return {"id": user_id, "name": "Alice"}
```

---

## Generics and Collections

### Built-in Collections (Python 3.9+)

```python
from typing import List, Dict, Set, Tuple

# Lists
names: list[str] = ["Alice", "Bob"]
numbers: list[int] = [1, 2, 3]
mixed: list[int | str] = [1, "two", 3]

# Dictionaries
user: dict[str, str | int] = {"name": "Alice", "age": 30}
scores: dict[str, float] = {"math": 95.5, "english": 88.0}

# Sets
unique_ids: set[int] = {1, 2, 3, 1}  # {1, 2, 3}

# Tuples (heterogeneous, fixed length)
point: tuple[int, int] = (10, 20)
record: tuple[str, int, bool] = ("Alice", 30, True)

# Variable-length tuples
values: tuple[int, ...] = (1, 2, 3, 4, 5)  # Any number of ints
```

### collections.abc for Abstract Types

```python
from collections.abc import Sequence, Mapping, Iterable

# Accepts any sequence (list, tuple, str, etc.)
def process_sequence(items: Sequence[int]) -> int:
    """Process any sequence of integers."""
    return sum(items)

# Accepts any mapping (dict, defaultdict, etc.)
def process_mapping(data: Mapping[str, int]) -> None:
    """Process any string-to-int mapping."""
    for key, value in data.items():
        print(f"{key}: {value}")

# Accepts any iterable (generator, list, etc.)
def consume_stream(stream: Iterable[str]) -> None:
    """Consume items from any iterable."""
    for item in stream:
        print(item)
```

---

## Optional and Union

### Union Types

```python
from typing import Union

# Union = multiple possible types
def process(value: Union[int, str]) -> str:
    """Process int or string."""
    return str(value)

# Python 3.10+ pipe syntax
def process(value: int | str) -> str:
    """Process int or string."""
    return str(value)

# Multiple union members
def handle_data(data: int | str | bytes) -> bytes:
    """Convert various types to bytes."""
    if isinstance(data, bytes):
        return data
    return str(data).encode()
```

### Optional Shorthand

```python
from typing import Optional

# Optional[T] = T | None
def get_env(key: str) -> Optional[str]:
    """Get environment variable or None."""
    import os
    return os.getenv(key)

# Equivalent to
def get_env(key: str) -> str | None:
    """Get environment variable or None."""
    import os
    return os.getenv(key)
```

---

## Type Aliases and NewType

### Type Aliases

```python
from typing import Dict, List, Tuple, Optional

# Alias for complex types
UserId = int
UserData = Dict[str, str | int]
Config = Dict[str, str | int | bool]

def get_user(user_id: UserId) -> Optional[UserData]:
    """Get user by ID."""
    return {"id": user_id, "name": "Alice", "age": 30}

def load_config(config_path: str) -> Config:
    """Load configuration from file."""
    return {"debug": True, "port": 8080}

# Alias for function types
Processor = Callable[[str], int]

def process_items(items: list[str], processor: Processor) -> list[int]:
    """Process items with a processor function."""
    return [processor(item) for item in items]
```

### NewType for Distinct Types

```python
from typing import NewType

# Distinct types that don't mix
UserId = NewType("UserId", int)
ProductId = NewType("ProductId", int)

# Type checker treats these as different
def get_user(user_id: UserId) -> dict:
    return {"id": user_id}

def get_product(product_id: ProductId) -> dict:
    return {"id": product_id}

# Type error: expected UserId, got ProductId
user = get_user(ProductId(123))  # ERROR

# Correct usage
user = get_user(UserId(123))  # OK
```

---

## Protocol and Structural Typing

### Protocol for Duck Typing

```python
from typing import Protocol, runtime_checkable

# Define a protocol (interface)
@runtime_checkable
class Drawable(Protocol):
    """Objects that can be drawn."""

    def draw(self) -> None: ...

    def resize(self, width: int, height: int) -> None: ...

# Usage
def render(obj: Drawable) -> None:
    """Render any drawable object."""
    obj.draw()
    obj.resize(100, 100)

# Any class with draw() and resize() methods matches
class Circle:
    def draw(self) -> None:
        print("Drawing circle")

    def resize(self, width: int, height: int) -> None:
        print(f"Resizing to {width}x{height}")

# Type checker accepts Circle
render(Circle())  # OK
```

### Protocol with Attributes

```python
from typing import Protocol, runtime_checkable

@runtime_checkable
class Named(Protocol):
    """Objects with a name attribute."""
    name: str

def greet(obj: Named) -> str:
    """Greet named object."""
    return f"Hello, {obj.name}!"

class Person:
    def __init__(self, name: str):
        self.name = name

# Works - Person has 'name' attribute
greet(Person("Alice"))  # OK
```

---

## Overloaded Functions

### Function Overloading

```python
from typing import overload, Union

@overload
def process(value: int) -> str:
    """Process integer value."""
    ...

@overload
def process(value: str) -> int:
    """Process string value."""
    ...

@overload
def process(value: list) -> dict:
    """Process list value."""
    ...

def process(value: Union[int, str, list]) -> Union[str, int, dict]:
    """Process value based on type."""
    if isinstance(value, int):
        return str(value)
    elif isinstance(value, str):
        return len(value)
    elif isinstance(value, list):
        return {"length": len(value)}
    else:
        raise TypeError(f"Unsupported type: {type(value)}")

# Type checker knows return type
result1: str = process(42)  # str
result2: int = process("hello")  # int
result3: dict = process([1, 2, 3])  # dict
```

---

## Async Type Hints

### Async Functions and Generators

```python
from typing import AsyncIterator, AsyncGenerator, Awaitable
from collections.abc import Coroutine

# Async function
async def fetch_data(url: str) -> dict:
    """Fetch data from URL."""
    import httpx
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        return response.json()

# Async iterator
async def stream_results(query: str) -> AsyncIterator[dict]:
    """Stream database results."""
    async with database.connect() as conn:
        async for row in conn.cursor(query):
            yield dict(row)

# Async generator with send and throw
async def process_stream(stream: AsyncIterator[str]) -> AsyncGenerator[str, None]:
    """Process async stream."""
    async for item in stream:
        yield f"Processed: {item}"

# Awaitable
def schedule_task(func: Coroutine[Any, Any, int]) -> Awaitable[int]:
    """Schedule async task."""
    return func
```

---

## Pydantic Integration

### Pydantic Models with Types

```python
from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from uuid import UUID, uuid4

class User(BaseModel):
    """User model with type validation."""

    id: UUID = Field(default_factory=uuid4)
    name: str = Field(..., min_length=1, max_length=100)
    email: str = Field(..., pattern=r"^[^@]+@[^@]+\.[^@]+$")
    age: int = Field(..., ge=0, le=150)
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)

    @field_validator("name")
    @classmethod
    def name_must_be_title_case(cls, v: str) -> str:
        """Ensure name is title case."""
        if not v.istitle():
            raise ValueError("Name must be title case")
        return v

# Usage
user = User(
    name="Alice Smith",
    email="alice@example.com",
    age=30,
)

# Type-aware model
user_dict = user.model_dump()
user_json = user.model_dump_json()
```

---

## Best Practices

1. **Be specific**: Use exact types over `Any`
2. **Use collections.abc**: Accept sequences, not just lists
3. **Document intent**: Type hints explain code purpose
4. **Test types**: Run mypy in CI/CD
5. **Avoid over-typing**: Simple functions might not need complex types

---

## Mypy Configuration

```toml
[tool.mypy]
python_version = "3.9"
strict = true  # For libraries
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
disallow_any_generics = true
```

For applications, relax strict mode:

```toml
[tool.mypy]
python_version = "3.9"
warn_return_any = true
warn_unused_configs = true
# Don't enforce strict mode for apps
```
