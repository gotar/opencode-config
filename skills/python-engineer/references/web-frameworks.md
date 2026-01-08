# Python Web Development Frameworks

Guide to choosing and using Python web frameworks, comparing FastAPI, Django, and Flask for different use cases.

## Table of Contents

1. [Framework Comparison](#framework-comparison)
2. [FastAPI](#fastapi)
3. [Django](#django)
4. [Flask](#flask)
5. [Choosing a Framework](#choosing-a-framework)
6. [Common Patterns](#common-patterns)

---

## Framework Comparison

| Feature | FastAPI | Django | Flask |
|---------|---------|--------|-------|
| **Type** | Async, modern | Full-stack, batteries included | Micro, minimal |
| **Performance** | Very fast (Starlette) | Moderate (WSGI) | Moderate (WSGI) |
| **Async Support** | ✅ Native | ⚠️ Limited (Django 4.1+) | ⚠️ Needs extensions |
| **Auto Docs** | ✅ OpenAPI/Swagger | ⚠️ DRS (Django REST) | ❌ Manual |
| **ORM** | SQLAlchemy (2nd-party) | Django ORM (built-in) | SQLAlchemy (3rd-party) |
| **Admin Panel** | ❌ No | ✅ Built-in | ❌ No |
| **Auth** | ✅ FastAPI Users | ✅ Built-in | ⚠️ Flask-Login |
| **Learning Curve** | Easy | Moderate | Very easy |
| **Best For** | APIs, microservices | Full-stack apps | Simple microservices |
| **Size** | Small | Large | Tiny |

---

## FastAPI

### Quick Start

**Installation**:
```bash
uv add fastapi uvicorn
```

**Minimal Example**:

```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="My API", version="1.0.0")

class Item(BaseModel):
    name: str
    price: float

@app.get("/")
async def root() -> dict:
    """Root endpoint."""
    return {"message": "Hello World"}

@app.get("/items/{item_id}")
async def read_item(item_id: int, q: str | None = None) -> dict:
    """Read item by ID."""
    return {"item_id": item_id, "q": q}

@app.post("/items", status_code=201)
async def create_item(item: Item) -> Item:
    """Create new item."""
    return item
```

**Run server**:
```bash
uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Dependency Injection

```python
from fastapi import Depends, HTTPException, status
from typing import AsyncGenerator
import httpx

# Database dependency
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Get database session."""
    async with async_session() as session:
        yield session

# HTTP client dependency
async def get_http_client() -> AsyncGenerator[httpx.AsyncClient, None]:
    """Get HTTP client."""
    async with httpx.AsyncClient() as client:
        yield client

# API key authentication
async def verify_api_key(x_api_key: str = Header(...)) -> str:
    """Verify API key."""
    if x_api_key != "secret-key":
        raise HTTPException(status_code=403, detail="Invalid API key")
    return x_api_key

# Use dependencies
@app.get("/protected")
async def protected_route(
    api_key: str = Depends(verify_api_key),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Protected route."""
    return {"message": "Authenticated"}
```

### Pydantic Models

```python
from pydantic import BaseModel, Field, EmailStr, HttpUrl
from datetime import datetime
from typing import Optional
from enum import Enum

class Status(str, Enum):
    """Item status."""
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"

class ItemBase(BaseModel):
    """Base item model."""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    price: float = Field(..., gt=0)
    status: Status = Status.DRAFT

class ItemCreate(ItemBase):
    """Item creation model."""
    pass

class ItemUpdate(BaseModel):
    """Item update model (all optional)."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    price: Optional[float] = Field(None, gt=0)
    status: Optional[Status] = None

class ItemResponse(ItemBase):
    """Item response model."""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Usage
@app.post("/items", response_model=ItemResponse, status_code=201)
async def create_item(
    item: ItemCreate,
    db: AsyncSession = Depends(get_db),
) -> ItemResponse:
    """Create item."""
    db_item = Item(**item.model_dump())
    db.add(db_item)
    await db.commit()
    await db.refresh(db_item)
    return db_item

@app.put("/items/{item_id}", response_model=ItemResponse)
async def update_item(
    item_id: int,
    item: ItemUpdate,
    db: AsyncSession = Depends(get_db),
) -> ItemResponse:
    """Update item."""
    db_item = await db.get(Item, item_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")

    for field, value in item.model_dump(exclude_unset=True).items():
        setattr(db_item, field, value)

    await db.commit()
    await db.refresh(db_item)
    return db_item
```

### Middleware

```python
from fastapi import Request
import time
import structlog

logger = structlog.get_logger(__name__)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all requests."""
    start_time = time.time()

    # Log request
    logger.info(
        "Request started",
        method=request.method,
        url=str(request.url),
        client=request.client.host if request.client else None,
    )

    # Process request
    response = await call_next(request)

    # Log response
    process_time = time.time() - start_time
    logger.info(
        "Request completed",
        status_code=response.status_code,
        process_time=process_time,
    )

    # Add custom header
    response.headers["X-Process-Time"] = str(process_time)
    return response

# CORS middleware
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## Django

### Quick Start

**Installation**:
```bash
uv add django djangorestframework
```

**Create project**:
```bash
uv run django-admin startproject myproject
cd myproject
uv run python manage.py startapp myapp
```

**Minimal example** (`views.py`):

```python
from django.http import JsonResponse
from django.views import View
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

# Function-based view
def hello(request):
    """Simple hello view."""
    return JsonResponse({"message": "Hello World"})

# Class-based view
class HelloView(View):
    """Hello view using class."""

    def get(self, request):
        """GET request."""
        return JsonResponse({"message": "Hello World"})

# REST API view
class ItemsListView(APIView):
    """List items."""

    def get(self, request):
        """GET list of items."""
        items = [{"id": 1, "name": "Item 1"}, {"id": 2, "name": "Item 2"}]
        return Response(items)

    def post(self, request):
        """POST new item."""
        data = request.data
        return Response(data, status=status.HTTP_201_CREATED)
```

### Django Models

```python
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator

class Category(models.Model):
    """Product category."""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.name

class Item(models.Model):
    """Product item."""
    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("published", "Published"),
        ("archived", "Archived"),
    ]

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.01)],
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="draft",
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="items",
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.name

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status", "created_at"]),
        ]
```

### Django REST Framework

```python
from rest_framework import serializers, viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

# Serializers
class ItemSerializer(serializers.ModelSerializer):
    """Item serializer."""
    category_name = serializers.CharField(source="category.name", read_only=True)

    class Meta:
        model = Item
        fields = ["id", "name", "description", "price", "status", "category_name"]
        read_only_fields = ["created_at", "updated_at"]

class ItemCreateSerializer(serializers.ModelSerializer):
    """Item create serializer (without ID)."""
    class Meta:
        model = Item
        fields = ["name", "description", "price", "status", "category"]

# ViewSets
class ItemViewSet(viewsets.ModelViewSet):
    """Item view set."""
    queryset = Item.objects.select_related("category").all()
    serializer_class = ItemSerializer

    def get_serializer_class(self):
        """Get appropriate serializer."""
        if self.action == "create":
            return ItemCreateSerializer
        return ItemSerializer

    @action(detail=True, methods=["post"])
    def publish(self, request, pk=None):
        """Publish item."""
        item = self.get_object()
        item.status = "published"
        item.save()
        serializer = self.get_serializer(item)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def published(self, request):
        """Get only published items."""
        items = self.queryset.filter(status="published")
        serializer = self.get_serializer(items, many=True)
        return Response(serializer.data)
```

### Django URLs

```python
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ItemViewSet

# Router for ViewSets
router = DefaultRouter()
router.register(r"items", ItemViewSet, basename="item")

urlpatterns = [
    path("api/", include(router.urls)),
    path("hello/", views.hello),
]
```

---

## Flask

### Quick Start

**Installation**:
```bash
uv add flask
```

**Minimal example**:

```python
from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route("/")
def hello():
    """Root endpoint."""
    return jsonify({"message": "Hello World"})

@app.route("/items/<int:item_id>")
def get_item(item_id):
    """Get item by ID."""
    return jsonify({"item_id": item_id})

@app.route("/items", methods=["POST"])
def create_item():
    """Create new item."""
    data = request.get_json()
    return jsonify(data), 201

if __name__ == "__main__":
    app.run(debug=True)
```

### Flask Blueprints

```python
from flask import Blueprint, jsonify

api = Blueprint("api", __name__, url_prefix="/api")

@api.route("/items")
def list_items():
    """List items."""
    items = [{"id": 1, "name": "Item 1"}]
    return jsonify(items)

@api.route("/items/<int:item_id>")
def get_item(item_id):
    """Get item."""
    return jsonify({"id": item_id, "name": "Item 1"})

# Register blueprint
from flask import Flask

app = Flask(__name__)
app.register_blueprint(api)
```

### Flask with Extensions

```python
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Configuration
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Extensions
db = SQLAlchemy(app)
ma = Marshmallow(app)

# Model
class Item(db.Model):
    """Item model."""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)

# Schema
class ItemSchema(ma.SQLAlchemyAutoSchema):
    """Item schema."""
    class Meta:
        model = Item
        load_instance = True

item_schema = ItemSchema()
items_schema = ItemSchema(many=True)
```

---

## Choosing a Framework

### Use FastAPI when:
- ✅ Building REST/GraphQL APIs
- ✅ Need async I/O performance
- ✅ Want automatic OpenAPI documentation
- ✅ Rapid development with type safety
- ✅ Building microservices
- ✅ Integrating with Pydantic

### Use Django when:
- ✅ Building full-stack web applications
- ✅ Need built-in admin interface
- ✅ Require robust authentication/permissions
- ✅ Want ORM and database migrations out of the box
- ✅ Building content-heavy sites
- ✅ Team familiar with Django patterns

### Use Flask when:
- ✅ Building simple microservices
- ✅ Need maximum flexibility
- ✅ Learning web frameworks
- ✅ Small, lightweight applications
- ✅ Want minimal dependencies
- ✅ Building prototypes

---

## Common Patterns

### Configuration Management

**FastAPI**:
```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "My App"
    debug: bool = False
    database_url: str

    class Config:
        env_file = ".env"

settings = Settings()

# Usage
app = FastAPI(title=settings.app_name)
```

**Django**:
```python
# settings.py
from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get("SECRET_KEY", "dev-key")
DEBUG = os.environ.get("DEBUG", "False") == "True"
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("DB_NAME"),
        "USER": os.environ.get("DB_USER"),
        "PASSWORD": os.environ.get("DB_PASSWORD"),
        "HOST": os.environ.get("DB_HOST", "localhost"),
        "PORT": os.environ.get("DB_PORT", "5432"),
    }
}
```

**Flask**:
```python
from dotenv import load_dotenv
import os

load_dotenv()

app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")
app.config["DATABASE_URL"] = os.environ.get("DATABASE_URL")
```

### Logging

**All frameworks** (structlog):
```python
import structlog

def configure_logging(debug: bool = False):
    """Configure structured logging."""
    import logging
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(level=level)

    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer() if not debug else structlog.dev.ConsoleRenderer(),
        ],
    )

configure_logging(debug=True)
logger = structlog.get_logger(__name__)
```

### Error Handling

**FastAPI**:
```python
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse

@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    """Handle ValueError."""
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": str(exc)},
    )
```

**Django**:
```python
from django.http import JsonResponse
from django.core.exceptions import ValidationError

def custom_exception_handler(exc, context):
    """Custom exception handler."""
    if isinstance(exc, ValidationError):
        return JsonResponse({"detail": str(exc)}, status=400)
    return drf_exception_handler(exc, context)
```

**Flask**:
```python
from werkzeug.exceptions import HTTPException
from flask import jsonify

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({"detail": "Not found"}), 404

@app.errorhandler(ValueError)
def value_error(error):
    """Handle ValueError."""
    return jsonify({"detail": str(error)}), 400
```

---

## Best Practices

1. **Use async for I/O**: Faster concurrent operations
2. **Validate input**: Pydantic (FastAPI) / DRF serializers (Django)
3. **Document APIs**: FastAPI auto-docs, Swagger/OpenAPI
4. **Handle errors gracefully**: Custom exception handlers
5. **Use middleware**: Logging, CORS, authentication
6. **Separate concerns**: Models, views, routes, business logic
7. **Write tests**: pytest-asyncio (FastAPI) / pytest-django
8. **Use environment variables**: Never hardcode secrets
