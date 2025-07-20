from robyn import Robyn, Request
from .utils import (
    with_random_errors,
    process_image_request,
    process_dual_image_request,
    process_form_image_request,
    process_dual_form_image_request,
    process_binary_stream_request,
    process_comma_separated_binary_request,
)

app = Robyn(__file__)


@app.post("/v1/register")
@with_random_errors
async def enroll(request: Request) -> dict | tuple:
    """
    Mock endpoint for register.
    Returns a JSON object with a new UUID, the processing time, and a timestamp.
    Additionally processes base64 image from request body and adjusts response based on image size.
    """
    return await process_image_request(request)


@app.post("/v1/search")
@with_random_errors
async def search(request: Request) -> dict | tuple:
    """
    Mock endpoint for searching.
    Returns a JSON object with a new UUID, the processing time, and a timestamp.
    Additionally processes base64 image from request body and adjusts response based on image size.
    """
    return await process_image_request(request)


@app.post("/v1/match")
@with_random_errors
async def match(request: Request) -> dict | tuple:
    """
    Mock endpoint for matching two images.
    Takes two base64 encoded images (image-1 and image-2) in the request body.
    Returns a JSON object with a new UUID, the processing time, a timestamp,
    the size of both images, and a similarity score.
    """
    return await process_dual_image_request(request)


@app.post("/v2/register")
@with_random_errors
async def enroll_v2(request: Request) -> dict | tuple:
    """
    Mock endpoint for register (v2).
    Accepts an image file via multipart form data with field name 'image'.
    Returns a JSON object with a new UUID, the processing time, and a timestamp.
    Additionally processes the image and adjusts response based on image size.
    """
    return await process_form_image_request(request)


@app.post("/v2/search")
@with_random_errors
async def search_v2(request: Request) -> dict | tuple:
    """
    Mock endpoint for searching (v2).
    Accepts an image file via multipart form data with field name 'image'.
    Returns a JSON object with a new UUID, the processing time, and a timestamp.
    Additionally processes the image and adjusts response based on image size.
    """
    return await process_form_image_request(request)


@app.post("/v2/match")
@with_random_errors
async def match_v2(request: Request) -> dict | tuple:
    """
    Mock endpoint for matching two images (v2).
    Accepts two image files via multipart form data with field names 'image-1' and 'image-2'.
    Returns a JSON object with a new UUID, the processing time, a timestamp,
    the size of both images, and a similarity score.
    """
    return await process_dual_form_image_request(request)


@app.post("/v3/register")
@with_random_errors
async def enroll_v3(request: Request) -> dict | tuple:
    """
    Mock endpoint for register (v3).
    Accepts an image as a binary stream directly in the request body.
    Returns a JSON object with a new UUID, the processing time, and a timestamp.
    Additionally processes the image and adjusts response based on image size.
    """
    return await process_binary_stream_request(request)


@app.post("/v3/search")
@with_random_errors
async def search_v3(request: Request) -> dict | tuple:
    """
    Mock endpoint for searching (v3).
    Accepts an image as a binary stream directly in the request body.
    Returns a JSON object with a new UUID, the processing time, and a timestamp.
    Additionally processes the image and adjusts response based on image size.
    """
    return await process_binary_stream_request(request)


@app.post("/v3/match")
@with_random_errors
async def match_v3(request: Request) -> dict | tuple:
    """
    Mock endpoint for matching two images (v3).
    Accepts two binary images separated by a comma directly in the request body.
    Returns a JSON object with a new UUID, the processing time, a timestamp,
    the size of both images, and a similarity score.
    """
    return await process_comma_separated_binary_request(request)


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
