"""
Database configuration and utilities.

This example shows:
- Async database session management
- Dependency injection
- Connection pooling
"""

from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
import asyncpg


# In real app, import models
# from models import Base

# Create async engine
DATABASE_URL = "postgresql+asyncpg://user:pass@localhost:5432/mydb"

engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)

# Create async session factory
async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Base class for models
Base = declarative_base()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for database session.

    Usage:
        @app.get("/items")
        async def list_items(db: AsyncSession = Depends(get_db)):
            result = await db.execute(select(Item))
            return result.scalars().all()
    """
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """Initialize database (create tables)."""
    # In real app, create all tables
    # async with engine.begin() as conn:
    #     await conn.run_sync(Base.metadata.create_all)

    print("Database initialized")


async def close_db() -> None:
    """Close database connections."""
    await engine.dispose()
    print("Database connections closed")


# Example usage
if __name__ == "__main__":
    import asyncio

    async def main():
        """Example usage."""
        # Initialize database
        await init_db()

        # Use database session
        async for session in get_db():
            # In real app, perform database operations
            # result = await session.execute(select(Item))
            # items = result.scalars().all()
            print("Database session created and committed")

        # Close database
        await close_db()

    asyncio.run(main())
