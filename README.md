# Mockr

A mock server for image processing endpoints with multiple API versions. Mockr simulates various image processing operations with realistic response times and random errors to help test client applications.

## Features

- Multiple API versions with different request formats
- Realistic response times based on image size
- Random errors (5% chance of server error, 5% chance of client error)
- Detailed mock responses with UUIDs, timestamps, and processing times
- Support for various image formats via Pillow

## API Endpoints

### V1 Endpoints (Base64 JSON)
- `/v1/register` - Register an image using base64 encoding in JSON
- `/v1/search` - Search using a base64 encoded image in JSON
- `/v1/match` - Match two base64 encoded images in JSON

### V2 Endpoints (Multipart Form)
- `/v2/register` - Register an image using multipart form data
- `/v2/search` - Search using an image in multipart form data
- `/v2/match` - Match two images in multipart form data

### V3 Endpoints (Binary Stream)
- `/v3/register` - Register an image using a binary stream
- `/v3/search` - Search using an image as a binary stream
- `/v3/match` - Match two images separated by a comma in a binary stream

### Other Endpoints
- `/info` - Get server information (service name, version, status)

## Response Format

All endpoints return JSON responses with the following common fields:
- `uuid` - A unique identifier for the request
- `timestamp` - ISO 8601 formatted timestamp in UTC
- `process_time` - Time taken to process the request in seconds
- `payload_size` - Size of the submitted image(s) in bytes

Additional fields vary by endpoint type:
- Register endpoints include quality scores and feature extraction details
- Search endpoints include mock search results with scores and rankings
- Match endpoints include similarity scores and match details

## Installation

```sh
# Install using pip
pip install mockr

# Or install using uv (recommended)
uv pip install mockr
```

## Running the Server

```sh
# Automatic optimization (recommended)
uv run mockr --fast

# For CPU-intensive applications
# Rule: processes = CPU cores, workers = 1
# Example: 8-core machine
uv run mockr --processes 8 --workers 1

# For I/O-intensive applications  
# Rule: processes = CPU cores / 2, workers = 2-4
# Example: 8-core machine
uv run mockr --processes 4 --workers 3

# For balanced applications
# Rule: processes = CPU cores / 2, workers = 2
# Example: 8-core machine
uv run mockr --processes 4 --workers 2

# Memory considerations
# Each process uses ~50-100MB base memory
# Monitor with: ps aux | grep python
```

## Example Requests

### V1 (Base64 JSON)

```sh
# Register an image
curl -X POST http://localhost:8848/v1/register \
  -H "Content-Type: application/json" \
  -d '{"image": "base64_encoded_image_data"}'

# Search with an image
curl -X POST http://localhost:8848/v1/search \
  -H "Content-Type: application/json" \
  -d '{"image": "base64_encoded_image_data"}'

# Match two images
curl -X POST http://localhost:8848/v1/match \
  -H "Content-Type: application/json" \
  -d '{"image-1": "base64_encoded_image_data_1", "image-2": "base64_encoded_image_data_2"}'
```

### V2 (Multipart Form)

```sh
# Register an image
curl -X POST http://localhost:8848/v2/register \
  -F "image=@path/to/image.jpg"

# Search with an image
curl -X POST http://localhost:8848/v2/search \
  -F "image=@path/to/image.jpg"

# Match two images
curl -X POST http://localhost:8848/v2/match \
  -F "image-1=@path/to/image1.jpg" \
  -F "image-2=@path/to/image2.jpg"
```

### V3 (Binary Stream)

```sh
# Register an image
curl -X POST http://localhost:8848/v3/register \
  --data-binary @path/to/image.jpg

# Search with an image
curl -X POST http://localhost:8848/v3/search \
  --data-binary @path/to/image.jpg

# Match two images (comma-separated binary)
# This requires preprocessing to join the images with a comma separator
```

## License

See the [LICENSE](LICENSE) file for details.