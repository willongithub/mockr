import datetime
import time
import uuid
from functools import wraps
from typing import Callable, Any

import random
import asyncio
from robyn import Robyn

app = Robyn(__file__)


def with_random_errors(func: Callable) -> Callable:
    """Decorator that adds random error responses to endpoints."""

    @wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> dict | tuple:
        seed = random.uniform(0, 100)
        if seed < 5:
            return {"description": "response failed."}, {}, 500
        elif seed > 95:
            return {"description": "request failed."}, {}, 400
        return await func(*args, **kwargs)

    return wrapper


async def generate_mock_response() -> dict:
    """Generates a mock response payload."""
    start_time = time.perf_counter()
    await asyncio.sleep(random.uniform(0.5, 1.5))  # Simulate a delay of around 1 second

    response_data = {
        "uuid": str(uuid.uuid4()),
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }
    end_time = time.perf_counter()
    response_data["process_time"] = f"{end_time - start_time:.6f}"
    return response_data


@app.post("/enroll")
@with_random_errors
async def enroll() -> dict | tuple:
    """
    Mock endpoint for enrollment.
    Returns a JSON object with a new UUID, the processing time, and a timestamp.
    """
    return await generate_mock_response()


@app.post("/search")
@with_random_errors
async def search() -> dict | tuple:
    """
    Mock endpoint for searching.
    Returns a JSON object with a new UUID, the processing time, and a timestamp.
    """
    return await generate_mock_response()


@app.post("/match")
@with_random_errors
async def match() -> dict | tuple:
    """
    Mock endpoint for matching.
    Returns a JSON object with a new UUID, the processing time, and a timestamp.
    """
    return await generate_mock_response()


@app.get("/info")
async def info() -> dict:
    """
    Returns basic information about the mock server.
    """
    return {"service": "mockr", "version": "1.0.0", "status": "running"}


def main() -> None:
    """Starts the Robyn server."""
    app.start(host="0.0.0.0", port=8848)


if __name__ == "__main__":
    main()
