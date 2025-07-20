import datetime
import time
import uuid
from functools import wraps
from typing import Callable, Any
import base64
import json

import random
import asyncio
from PIL import Image
import io


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


def process_base64_image(image_data: str) -> tuple[int, dict] | tuple[bytes, int]:
    """
    Process a base64 encoded image string and return the decoded image and its size.
    Returns either (decoded_image, size) on success or (status_code, error_dict) on failure.
    """
    if not image_data:
        return 400, {"error": "Missing image data"}

    try:
        # Remove data URI prefix if present
        if image_data.startswith("data:"):
            image_data = image_data.split(",", 1)[1]

        # Add padding if needed
        padding = 4 - (len(image_data) % 4) if len(image_data) % 4 else 0
        image_data += "=" * padding

        decoded_image = base64.b64decode(image_data)
        image_size = len(decoded_image)

        # Try to open the image with Pillow to validate it
        try:
            Image.open(io.BytesIO(decoded_image))
        except Exception as e:
            return 400, {"error": f"Invalid image format: {str(e)}"}

        return decoded_image, image_size
    except Exception as e:
        return 500, {"error": f"Failed to process image: {str(e)}"}


async def process_image_request(request) -> dict | tuple:
    """
    Processes a request with base64 image data and returns appropriate response.
    Returns either a success response with image processing info or an error response.
    """
    try:
        body = request.json()
        image_data = body.get("image", "")

        result = process_base64_image(image_data)
        if isinstance(result[0], int):  # Error case
            return result

        decoded_image, image_size = result
        response = await generate_mock_response(delay_factor=image_size / 10000)
        response["payload_size"] = image_size

        # Add additional mock data based on endpoint
        if "register" in str(request.url):
            # For register endpoint
            response["registration"] = {
                "status": "success",
                "id": str(uuid.uuid4()),
                "quality_score": round(random.uniform(0.6, 1.0), 2),
                "features_extracted": random.randint(80, 150),
            }
        elif "search" in str(request.url):
            # For search endpoint
            num_results = random.randint(1, 5)
            response["search_results"] = [
                {
                    "id": str(uuid.uuid4()),
                    "score": round(random.uniform(0.5, 0.99), 4),
                    "rank": i + 1,
                }
                for i in range(num_results)
            ]
            response["total_matches"] = num_results
            response["search_time_ms"] = round(random.uniform(50, 500), 2)

        return response
    except json.JSONDecodeError as e:
        return 500, {"error": f"Invalid JSON: {str(e)}"}


async def process_dual_image_request(request) -> dict | tuple:
    """
    Processes a request with two base64 images (image-1 and image-2) and returns appropriate response.
    Returns either a success response with combined image processing info or an error response.
    """
    try:
        body = request.json()
        image1_data = body.get("image-1", "")
        image2_data = body.get("image-2", "")

        # Process first image
        result1 = process_base64_image(image1_data)
        if isinstance(result1[0], int):  # Error case
            return result1

        # Process second image
        result2 = process_base64_image(image2_data)
        if isinstance(result2[0], int):  # Error case
            return result2

        # Calculate combined size and delay factor
        _, image1_size = result1
        _, image2_size = result2
        total_size = image1_size + image2_size

        # Generate response with delay proportional to combined size
        response = await generate_mock_response(delay_factor=total_size / 15000)
        response["payload_size"] = total_size

        # Add a similarity score (random for mock purposes)
        response["similarity_score"] = round(random.uniform(0, 1), 4)

        # Add additional mock data
        response["match_details"] = {
            "confidence": round(random.uniform(0.7, 0.99), 4),
            "match_points": random.randint(10, 100),
            "processing_level": random.choice(["basic", "enhanced", "deep"]),
            "algorithm": random.choice(
                ["eigenfaces", "fisherfaces", "LBPH", "CNN", "SIFT"]
            ),
        }

        return response
    except json.JSONDecodeError as e:
        return 500, {"error": f"Invalid JSON: {str(e)}"}


async def process_form_image(request) -> tuple[int, dict] | tuple[bytes, int]:
    """
    Process an image from multipart form data.
    Returns either (image_bytes, size) on success or (status_code, error_dict) on failure.
    """
    try:
        form_data = await request.form()
        if "image" not in form_data:
            return 400, {"error": "Missing image in form data"}

        image_file = form_data["image"]
        image_bytes = await image_file.read()
        image_size = len(image_bytes)

        # Try to open the image with Pillow to validate it
        try:
            Image.open(io.BytesIO(image_bytes))
        except Exception as e:
            return 400, {"error": f"Invalid image format: {str(e)}"}

        return image_bytes, image_size
    except Exception as e:
        return 500, {"error": f"Failed to process image: {str(e)}"}


async def process_dual_form_images(
    request,
) -> tuple[int, dict] | tuple[tuple[bytes, int], tuple[bytes, int]]:
    """
    Process two images from multipart form data.
    Returns either (image1_data, image2_data) on success or (status_code, error_dict) on failure.
    """
    try:
        form_data = await request.form()

        # Check for first image
        if "image-1" not in form_data:
            return 400, {"error": "Missing image-1 in form data"}

        # Check for second image
        if "image-2" not in form_data:
            return 400, {"error": "Missing image-2 in form data"}

        # Process first image
        image1_file = form_data["image-1"]
        image1_bytes = await image1_file.read()
        image1_size = len(image1_bytes)

        # Try to open the first image with Pillow to validate it
        try:
            Image.open(io.BytesIO(image1_bytes))
        except Exception as e:
            return 400, {"error": f"Invalid format for image-1: {str(e)}"}

        # Process second image
        image2_file = form_data["image-2"]
        image2_bytes = await image2_file.read()
        image2_size = len(image2_bytes)

        # Try to open the second image with Pillow to validate it
        try:
            Image.open(io.BytesIO(image2_bytes))
        except Exception as e:
            return 400, {"error": f"Invalid format for image-2: {str(e)}"}

        return (image1_bytes, image1_size), (image2_bytes, image2_size)
    except Exception as e:
        return 500, {"error": f"Failed to process images: {str(e)}"}


async def process_form_image_request(request) -> dict | tuple:
    """
    Processes a request with an image from form data and returns appropriate response.
    Returns either a success response with image processing info or an error response.
    """
    result = await process_form_image(request)
    if isinstance(result[0], int):  # Error case
        return result

    _, image_size = result
    response = await generate_mock_response(delay_factor=image_size / 10000)
    response["payload_size"] = image_size

    # Add additional mock data to match v1 response
    if "register" in str(request.url):
        # For register endpoint
        response["registration"] = {
            "status": "success",
            "id": str(uuid.uuid4()),
            "quality_score": round(random.uniform(0.6, 1.0), 2),
            "features_extracted": random.randint(80, 150),
        }
    elif "search" in str(request.url):
        # For search endpoint
        num_results = random.randint(1, 5)
        response["search_results"] = [
            {
                "id": str(uuid.uuid4()),
                "score": round(random.uniform(0.5, 0.99), 4),
                "rank": i + 1,
            }
            for i in range(num_results)
        ]
        response["total_matches"] = num_results
        response["search_time_ms"] = round(random.uniform(50, 500), 2)

    return response


async def process_dual_form_image_request(request) -> dict | tuple:
    """
    Processes a request with two images from form data and returns appropriate response.
    Returns either a success response with combined image processing info or an error response.
    """
    result = await process_dual_form_images(request)
    if isinstance(result[0], int):  # Error case
        return result

    (_, image1_size), (_, image2_size) = result
    total_size = image1_size + image2_size

    # Generate response with delay proportional to combined size
    response = await generate_mock_response(delay_factor=total_size / 15000)
    response["payload_size"] = total_size

    # Add a similarity score (random for mock purposes)
    response["similarity_score"] = round(random.uniform(0, 1), 4)

    # Add additional mock data to match v1 response
    response["match_details"] = {
        "confidence": round(random.uniform(0.7, 0.99), 4),
        "match_points": random.randint(10, 100),
        "processing_level": random.choice(["basic", "enhanced", "deep"]),
        "algorithm": random.choice(
            ["eigenfaces", "fisherfaces", "LBPH", "CNN", "SIFT"]
        ),
    }

    return response


async def process_binary_stream(request) -> tuple[int, dict] | tuple[bytes, int]:
    """
    Process a binary stream from the request body.
    Returns either (image_bytes, size) on success or (status_code, error_dict) on failure.
    """
    try:
        # Read the binary data directly from the request body
        image_bytes = await request.body()

        if not image_bytes:
            return 400, {"error": "Missing binary data in request body"}

        # Try to open the image with Pillow to validate it
        try:
            Image.open(io.BytesIO(image_bytes))
        except Exception as e:
            return 400, {"error": f"Invalid image format: {str(e)}"}

        image_size = len(image_bytes)
        return image_bytes, image_size
    except Exception as e:
        return 500, {"error": f"Failed to process binary stream: {str(e)}"}


async def process_binary_stream_request(request) -> dict | tuple:
    """
    Processes a request with binary stream data and returns appropriate response.
    Returns either a success response with image processing info or an error response.
    """
    result = await process_binary_stream(request)
    if isinstance(result[0], int):  # Error case
        return result

    _, image_size = result
    response = await generate_mock_response(delay_factor=image_size / 10000)
    response["payload_size"] = image_size

    # Add additional mock data based on endpoint
    if "register" in str(request.url):
        # For register endpoint
        response["registration"] = {
            "status": "success",
            "id": str(uuid.uuid4()),
            "quality_score": round(random.uniform(0.6, 1.0), 2),
            "features_extracted": random.randint(80, 150),
        }
    elif "search" in str(request.url):
        # For search endpoint
        num_results = random.randint(1, 5)
        response["search_results"] = [
            {
                "id": str(uuid.uuid4()),
                "score": round(random.uniform(0.5, 0.99), 4),
                "rank": i + 1,
            }
            for i in range(num_results)
        ]
        response["total_matches"] = num_results
        response["search_time_ms"] = round(random.uniform(50, 500), 2)

    return response


async def process_comma_separated_binary_images(
    request,
) -> tuple[int, dict] | tuple[tuple[bytes, int], tuple[bytes, int]]:
    """
    Process two binary images separated by a comma from the request body.
    Returns either ((image1_bytes, image1_size), (image2_bytes, image2_size)) on success
    or (status_code, error_dict) on failure.
    """
    try:
        # Read the binary data directly from the request body
        binary_data = await request.body()

        if not binary_data:
            return 400, {"error": "Missing binary data in request body"}

        # Find the comma separator
        try:
            # Split the binary data at the first comma
            comma_index = binary_data.find(b",")
            if comma_index == -1:
                return 400, {"error": "No comma separator found between images"}

            image1_bytes = binary_data[:comma_index]
            image2_bytes = binary_data[comma_index + 1 :]

            # Validate both parts as images
            try:
                Image.open(io.BytesIO(image1_bytes))
                Image.open(io.BytesIO(image2_bytes))
            except Exception as e:
                return 400, {
                    "error": f"Invalid image format in one or both parts: {str(e)}"
                }

            image1_size = len(image1_bytes)
            image2_size = len(image2_bytes)

            return (image1_bytes, image1_size), (image2_bytes, image2_size)
        except Exception as e:
            return 400, {"error": f"Failed to split binary data at comma: {str(e)}"}

    except Exception as e:
        return 500, {"error": f"Failed to process binary images: {str(e)}"}


async def process_comma_separated_binary_request(request) -> dict | tuple:
    """
    Processes a request with two binary images separated by a comma and returns appropriate response.
    Returns either a success response with combined image processing info or an error response.
    """
    result = await process_comma_separated_binary_images(request)
    if isinstance(result[0], int):  # Error case
        return result

    (_, image1_size), (_, image2_size) = result
    total_size = image1_size + image2_size

    # Generate response with delay proportional to combined size
    response = await generate_mock_response(delay_factor=total_size / 15000)
    response["payload_size"] = total_size

    # Add a similarity score (random for mock purposes)
    response["similarity_score"] = round(random.uniform(0, 1), 4)

    # Add additional mock data
    response["match_details"] = {
        "confidence": round(random.uniform(0.7, 0.99), 4),
        "match_points": random.randint(10, 100),
        "processing_level": random.choice(["basic", "enhanced", "deep"]),
        "algorithm": random.choice(
            ["eigenfaces", "fisherfaces", "LBPH", "CNN", "SIFT"]
        ),
    }

    return response


async def generate_mock_response(delay_factor: float = 1.0) -> dict:
    """Generates a mock response payload."""
    start_time = time.perf_counter()
    base_delay = random.uniform(0.5, 1.5)
    adjusted_delay = base_delay * delay_factor
    await asyncio.sleep(adjusted_delay)

    response_data = {
        "uuid": str(uuid.uuid4()),
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }
    end_time = time.perf_counter()
    response_data["process_time"] = f"{end_time - start_time:.6f}"
    return response_data
