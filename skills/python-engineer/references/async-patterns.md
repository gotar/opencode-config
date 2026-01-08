# Python Async Best Practices

Comprehensive guide to async/await patterns in Python, covering when to use async, common patterns, and performance optimization.

## Table of Contents

1. [When to Use Async](#when-to-use-async)
2. [Basic Async Patterns](#basic-async-patterns)
3. [Concurrent Execution](#concurrent-execution)
4. [Async Context Managers](#async-context-managers)
5. [Async Iterators and Generators](#async-iterators-and-generators)
6. [Error Handling in Async](#error-handling-in-async)
7. [Performance Considerations](#performance-considerations)
8. [Testing Async Code](#testing-async-code)
9. [Common Pitfalls](#common-pitfalls)

---

## When to Use Async

**Use async for**:
- I/O-bound operations (HTTP requests, database queries)
- Network operations (websockets, streams)
- Concurrent tasks without CPU bottlenecks
- Applications handling many simultaneous connections

**Don't use async for**:
- CPU-intensive operations (use multiprocessing)
- Simple synchronous code
- When libraries don't support async

---

## Basic Async Patterns

### Async Functions

```python
import asyncio
import httpx

# Basic async function
async def fetch_data(url: str) -> dict:
    """Fetch data from URL."""
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        return response.json()

# Call async function
async def main() -> None:
    data = await fetch_data("https://api.example.com/data")
    print(data)

# Run async function
if __name__ == "__main__":
    asyncio.run(main())
```

### Async Sleep

```python
import asyncio

async def task(name: str, delay: float) -> None:
    """Task with delay."""
    print(f"{name}: Started")
    await asyncio.sleep(delay)
    print(f"{name}: Completed after {delay}s")

async def main() -> None:
    """Run tasks concurrently."""
    # Run concurrently
    await asyncio.gather(
        task("Task 1", 1.0),
        task("Task 2", 0.5),
        task("Task 3", 1.5),
    )

if __name__ == "__main__":
    asyncio.run(main())
```

---

## Concurrent Execution

### asyncio.gather

```python
import asyncio
import httpx

async def fetch_url(url: str) -> dict:
    """Fetch single URL."""
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        return response.json()

async def fetch_multiple(urls: list[str]) -> list[dict]:
    """Fetch multiple URLs concurrently."""
    async with httpx.AsyncClient() as client:
        tasks = [client.get(url) for url in urls]
        responses = await asyncio.gather(*tasks, return_exceptions=True)

        # Handle exceptions
        results = []
        for i, response in enumerate(responses):
            if isinstance(response, Exception):
                print(f"Error fetching {urls[i]}: {response}")
            else:
                results.append(response.json())

        return results
```

### asyncio.create_task

```python
import asyncio

async def background_task(name: str, duration: float) -> str:
    """Run background task."""
    await asyncio.sleep(duration)
    return f"{name} completed after {duration}s"

async def main() -> None:
    """Run background tasks."""
    # Create tasks (start running immediately)
    task1 = asyncio.create_task(background_task("Task 1", 1.0))
    task2 = asyncio.create_task(background_task("Task 2", 0.5))
    task3 = asyncio.create_task(background_task("Task 3", 1.5))

    # Do other work while tasks run
    print("Tasks started, doing other work...")
    await asyncio.sleep(0.3)

    # Wait for tasks to complete
    results = await asyncio.gather(task1, task2, task3)
    print(f"Results: {results}")

if __name__ == "__main__":
    asyncio.run(main())
```

### asyncio.wait (with timeout)

```python
import asyncio

async def task(name: str, duration: float) -> str:
    """Task with duration."""
    await asyncio.sleep(duration)
    return f"{name} completed"

async def main() -> None:
    """Run tasks with timeout."""
    tasks = [
        asyncio.create_task(task("Task 1", 2.0)),
        asyncio.create_task(task("Task 2", 1.0)),
        asyncio.create_task(task("Task 3", 3.0)),
    ]

    try:
        # Wait for first task to complete or timeout
        done, pending = await asyncio.wait(
            tasks,
            timeout=1.5,
            return_when=asyncio.FIRST_COMPLETED,
        )

        print("Completed tasks:")
        for task in done:
            print(f"  - {task.result()}")

        # Cancel pending tasks
        for task in pending:
            task.cancel()

    except asyncio.TimeoutError:
        print("Timeout reached")

if __name__ == "__main__":
    asyncio.run(main())
```

---

## Async Context Managers

### Custom Async Context Manager

```python
import asyncio
from typing import AsyncIterator

class DatabaseConnection:
    """Async database connection manager."""

    def __init__(self, dsn: str):
        self.dsn = dsn
        self.conn = None

    async def __aenter__(self) -> "DatabaseConnection":
        """Enter context - open connection."""
        print(f"Connecting to {self.dsn}...")
        await asyncio.sleep(0.1)  # Simulate connection
        self.conn = "connection-obj"
        print("Connected!")
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit context - close connection."""
        print("Closing connection...")
        await asyncio.sleep(0.1)  # Simulate close
        self.conn = None
        print("Closed!")

    async def execute(self, query: str) -> list[dict]:
        """Execute query."""
        print(f"Executing: {query}")
        await asyncio.sleep(0.2)
        return [{"result": "data"}]

# Usage
async def main() -> None:
    """Use async context manager."""
    async with DatabaseConnection("postgresql://localhost/db") as db:
        results = await db.execute("SELECT * FROM users")
        print(f"Results: {results}")

if __name__ == "__main__":
    asyncio.run(main())
```

### contextlib.asynccontextmanager

```python
from contextlib import asynccontextmanager
from typing import AsyncIterator

@asynccontextmanager
async def timer(name: str) -> AsyncIterator[None]:
    """Context manager for timing operations."""
    import time
    start = time.time()
    print(f"Timer '{name}' started")
    try:
        yield
    finally:
        elapsed = time.time() - start
        print(f"Timer '{name}' elapsed: {elapsed:.2f}s")

# Usage
async def main() -> None:
    """Use timer context manager."""
    async with timer("operation"):
        await asyncio.sleep(1.0)
        await asyncio.sleep(0.5)

if __name__ == "__main__":
    asyncio.run(main())
```

---

## Async Iterators and Generators

### Async Iterator

```python
from typing import AsyncIterator

async def read_lines(path: str) -> AsyncIterator[str]:
    """Async file line iterator."""
    import aiofiles
    async with aiofiles.open(path, mode="r") as file:
        async for line in file:
            yield line.strip()

# Usage
async def main() -> None:
    """Consume async iterator."""
    async for line in read_lines("data.txt"):
        print(line)

if __name__ == "__main__":
    asyncio.run(main())
```

### Async Generator

```python
from typing import AsyncGenerator

async def generate_numbers(count: int) -> AsyncGenerator[int, None]:
    """Generate numbers asynchronously."""
    for i in range(count):
        await asyncio.sleep(0.1)  # Simulate work
        yield i

async def process_stream(stream: AsyncGenerator[int, None]) -> None:
    """Process async generator."""
    async for number in stream:
        print(f"Processing: {number}")

# Usage
async def main() -> None:
    """Use async generator."""
    numbers = generate_numbers(5)
    await process_stream(numbers)

if __name__ == "__main__":
    asyncio.run(main())
```

---

## Error Handling in Async

### Handling Exceptions

```python
import asyncio

async def risky_task(name: str, fail: bool = False) -> str:
    """Task that may fail."""
    await asyncio.sleep(0.1)
    if fail:
        raise ValueError(f"{name} failed!")
    return f"{name} succeeded"

async def main() -> None:
    """Handle exceptions in async tasks."""
    tasks = [
        risky_task("Task 1", fail=False),
        risky_task("Task 2", fail=True),
        risky_task("Task 3", fail=False),
    ]

    # gather with return_exceptions=True
    results = await asyncio.gather(*tasks, return_exceptions=True)

    for i, result in enumerate(results):
        if isinstance(result, Exception):
            print(f"Task {i + 1} failed: {result}")
        else:
            print(f"Task {i + 1}: {result}")

if __name__ == "__main__":
    asyncio.run(main())
```

### Async try/except/finally

```python
import asyncio

async def with_cleanup() -> None:
    """Async code with proper cleanup."""
    resource = None
    try:
        # Acquire resource
        resource = await acquire_resource()
        print("Resource acquired")

        # Do work
        result = await do_work(resource)
        print(f"Work done: {result}")

    except ValueError as e:
        print(f"Value error: {e}")
        raise

    except Exception as e:
        print(f"Unexpected error: {e}")
        raise

    finally:
        # Always cleanup
        if resource:
            await release_resource(resource)
            print("Resource released")

async def acquire_resource() -> str:
    """Acquire resource."""
    await asyncio.sleep(0.1)
    return "resource-obj"

async def release_resource(resource: str) -> None:
    """Release resource."""
    await asyncio.sleep(0.1)

async def do_work(resource: str) -> str:
    """Do work with resource."""
    await asyncio.sleep(0.2)
    return "work-result"

if __name__ == "__main__":
    asyncio.run(with_cleanup())
```

---

## Performance Considerations

### Avoid Blocking the Event Loop

```python
import asyncio

# ❌ BAD: Blocking call in async function
async def bad_blocking() -> None:
    """This blocks the event loop."""
    time.sleep(2.0)  # BLOCKS!
    print("Done")

# ✅ GOOD: Use asyncio.sleep
async def good_nonblocking() -> None:
    """This doesn't block."""
    await asyncio.sleep(2.0)  # Non-blocking
    print("Done")

# ✅ GOOD: Run blocking code in executor
async def run_blocking_in_executor() -> None:
    """Run blocking code in thread pool."""
    import time
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, time.sleep, 2.0)
    print("Done")
```

### Limit Concurrency

```python
import asyncio

async def worker(name: str, queue: asyncio.Queue) -> None:
    """Worker processing items from queue."""
    while True:
        item = await queue.get()
        try:
            print(f"{name}: Processing {item}")
            await asyncio.sleep(0.5)  # Simulate work
            print(f"{name}: Completed {item}")
        finally:
            queue.task_done()

async def main() -> None:
    """Run workers with limited concurrency."""
    queue = asyncio.Queue(maxsize=10)

    # Create workers
    workers = [
        asyncio.create_task(worker(f"Worker {i}", queue))
        for i in range(3)  # 3 concurrent workers
    ]

    # Add items to queue
    for i in range(10):
        await queue.put(f"Item {i}")

    # Wait for all items to be processed
    await queue.join()

    # Cancel workers
    for worker in workers:
        worker.cancel()

if __name__ == "__main__":
    asyncio.run(main())
```

---

## Testing Async Code

### pytest-asyncio

```python
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_fetch_data():
    """Test async function."""
    from myapp.main import fetch_data
    data = await fetch_data("https://api.example.com/data")
    assert "results" in data

@pytest.mark.asyncio
async def test_concurrent_fetch():
    """Test concurrent async operations."""
    urls = [
        "https://api.example.com/data1",
        "https://api.example.com/data2",
    ]
    results = await fetch_multiple(urls)
    assert len(results) == 2
```

### Async Fixtures

```python
import pytest
from httpx import AsyncClient

@pytest.fixture
async def async_client():
    """Async HTTP client fixture."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

@pytest.mark.asyncio
async def test_api_endpoint(async_client: AsyncClient):
    """Test API endpoint with async client."""
    response = await async_client.get("/api/users")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
```

---

## Common Pitfalls

### 1. Forgetting `await`

```python
# ❌ BAD: Forgot await
async def bad_example():
    result = fetch_data()  # Returns coroutine, not result
    print(result)  # <coroutine object>

# ✅ GOOD: Use await
async def good_example():
    result = await fetch_data()
    print(result)
```

### 2. Mixing sync and async

```python
# ❌ BAD: Calling async from sync
def bad_sync():
    result = await async_function()  # Syntax error

# ✅ GOOD: Use asyncio.run
def good_sync():
    result = asyncio.run(async_function())
    print(result)
```

### 3. Not closing resources

```python
# ❌ BAD: Not closing client
async def bad_fetch(url: str):
    client = httpx.AsyncClient()
    response = await client.get(url)
    return response.json()

# ✅ GOOD: Use context manager
async def good_fetch(url: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        return response.json()
```

### 4. Overusing async

```python
# ❌ BAD: Async for simple CPU task
async def bad_calculate(n: int) -> int:
    # No I/O, no benefit from async
    return sum(range(n))

# ✅ GOOD: Sync for CPU task
def good_calculate(n: int) -> int:
    return sum(range(n))
```

---

## Best Practices

1. **Use async for I/O-bound**: Network, database, file operations
2. **Use sync for CPU-bound**: Calculations, data processing
3. **Use context managers**: Proper resource cleanup
4. **Handle exceptions**: Use `return_exceptions=True` in gather
5. **Limit concurrency**: Use semaphores or queues
6. **Test async code**: Use pytest-asyncio
7. **Avoid blocking**: Don't use `time.sleep()` in async code
