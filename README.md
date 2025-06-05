# Mock Python Server

A simple Flask-based mock server that simulates job processing with authentication and polling functionality.

## Features

- **Authentication**: Bearer token authentication required
- **Job Submission**: Submit array of string IDs for processing
- **Job Polling**: Poll job status with realistic progression simulation
- **Thread-Safe**: Concurrent request handling with proper synchronization

## API Endpoints

### POST `/run`

Submit a new job for processing.

**Headers:**
```
Authorization: Bearer <your-token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "input": ["some-id-1", "some-id-2", "some-id-3"]
}
```

**Success Response (200):**
```json
{
  "id": "60902e6c-08a1-426e-9cb9-9eaec90f5e2b-u1",
  "status": "IN_PROGRESS"
}
```

**Error Responses:**
- `401 Unauthorized`: Missing or invalid authentication
- `400 Bad Request`: Invalid input (must be array of strings)

### GET `/status/<job_id>`

Poll the status of a submitted job.

**Response Behavior:**
- **First 3 polls**: Returns `IN_PROGRESS` status
- **4th+ polls**: Returns `COMPLETED` status with output

**In Progress Response:**
```json
{
  "id": "60902e6c-08a1-426e-9cb9-9eaec90f5e2b-u1",
  "status": "IN_PROGRESS"
}
```

**Completed Response:**
```json
{
  "id": "60902e6c-08a1-426e-9cb9-9eaec90f5e2b-u1",
  "status": "COMPLETED",
  "output": {
    "uuid": "random-uuid-here"
  }
}
```

**Error Response:**
- `404 Not Found`: Job ID not found

### GET `/health`

Health check endpoint.

**Response:**
```json
{
  "status": "healthy"
}
```

## Quick Start

### Using Make (Recommended)

```bash
# Run the server (sets up venv, installs deps, and starts server)
make run

# Other available commands
make help     # Show available commands
make setup    # Create virtual environment only
make install  # Install dependencies only
make clean    # Remove virtual environment
```

### Manual Setup

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Linux/Mac
# or
venv\Scripts\activate     # On Windows

# Install dependencies
pip install -r requirements.txt

# Run server
python index.py
```

## Usage Examples

### Submit a Job
```bash
curl -X POST http://localhost:5000/run \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer my-secret-token" \
  -d '{"input": ["id1", "id2", "id3"]}'
```

### Poll Job Status
```bash
# Replace YOUR_JOB_ID with the ID returned from /run
curl http://localhost:5000/status/YOUR_JOB_ID
```

### Test Authentication
```bash
# This should return 401 Unauthorized
curl -X POST http://localhost:5000/run \
  -H "Content-Type: application/json" \
  -d '{"input": ["id1", "id2", "id3"]}'
```

### Test Input Validation
```bash
# This should return 400 Bad Request
curl -X POST http://localhost:5000/run \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer my-token" \
  -d '{"input": "not-an-array"}'
```

## Configuration

The server runs on:
- **Host**: `0.0.0.0` (accessible from any interface)
- **Port**: `5000`
- **Debug Mode**: Enabled (for development)

## Dependencies

- Flask 2.3.3

## Project Structure

```
.
├── index.py           # Main server application
├── requirements.txt   # Python dependencies
├── Makefile          # Build and run commands
└── README_mock_server.md  # This documentation
```

## Development Notes

- Job data is stored in memory and will be lost when the server restarts
- The server is configured for development with debug mode enabled
- Thread-safe operations ensure proper handling of concurrent requests
- UUIDs are generated with "-u1" suffix as specified in the requirements 