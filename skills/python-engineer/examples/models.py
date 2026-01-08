"""
Pydantic models for FastAPI example.

This example shows:
- Base models with inheritance
- Field validation
- Enum types
- Optional fields
- Read-only fields
"""

from pydantic import BaseModel, Field, HttpUrl, field_validator
from typing import Optional, List
from enum import Enum


class Status(str, Enum):
    """Item status."""

    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class ItemBase(BaseModel):
    """Base item model with common fields."""

    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(
        None,
        max_length=500,
        description="Item description",
    )
    price: float = Field(
        ...,
        gt=0,
        description="Price must be greater than 0",
    )
    status: Status = Field(
        default=Status.DRAFT,
        description="Item status",
    )

    @field_validator("name")
    @classmethod
    def name_must_not_be_empty(cls, v: str) -> str:
        """Ensure name is not empty after stripping."""
        if not v.strip():
            raise ValueError("Name cannot be empty or whitespace")
        return v.strip()


class ItemCreate(ItemBase):
    """Item creation model."""

    pass


class ItemUpdate(BaseModel):
    """Item update model (all fields optional)."""

    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    price: Optional[float] = Field(None, gt=0)
    status: Optional[Status] = None


class Item(ItemBase):
    """Item model with ID (used in responses)."""

    id: int = Field(..., description="Unique item ID")
    created_at: str = Field(..., description="Creation timestamp")
    updated_at: str = Field(..., description="Last update timestamp")

    class Config:
        """Pydantic config."""

        from_attributes = True  # Allow ORM objects
        json_schema_extra = {
            "examples": [
                {
                    "id": 1,
                    "name": "Example Item",
                    "description": "An example item",
                    "price": 99.99,
                    "status": "published",
                    "created_at": "2024-01-01T00:00:00Z",
                    "updated_at": "2024-01-01T00:00:00Z",
                }
            ]
        }


class ItemListResponse(BaseModel):
    """Paginated item list response."""

    items: List[Item]
    total: int = Field(..., description="Total number of items")
    skip: int = Field(0, description="Number of items skipped")
    limit: int = Field(100, description="Number of items per page")


class ErrorResponse(BaseModel):
    """Error response model."""

    detail: str = Field(..., description="Error message")
    status_code: int = Field(..., description="HTTP status code")


# Example usage
if __name__ == "__main__":
    # Create item
    item_create = ItemCreate(
        name="Example Item",
        description="An example item",
        price=99.99,
        status=Status.PUBLISHED,
    )

    print("Created item:")
    print(f"  Name: {item_create.name}")
    print(f"  Status: {item_create.status}")

    # Serialize to JSON
    json_str = item_create.model_dump_json()
    print(f"\nJSON: {json_str}")

    # Parse from JSON
    parsed = ItemCreate.model_validate_json(json_str)
    print(f"\nParsed: {parsed}")
