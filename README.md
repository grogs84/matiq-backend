# Matiq Backend

A modern FastAPI backend application for MatIQ, a wrestling analytics platform.

## Setup

1. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
# Copy and edit environment variables
cp .env.example .env
# Edit .env with your Supabase credentials
```

4. Run the application:
```bash
python main.py
```

The API will be available at:
- http://localhost:8000 - API root
- http://localhost:8000/docs - Interactive API documentation
- http://localhost:8000/health - Health check endpoint

## Authentication

The application includes basic user authentication via Supabase. To use authentication:

### Login Endpoint

**POST** `/api/v1/auth/login`

Authenticate a user with email and password.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "userpassword"
}
```

**Response (Success):**
```json
{
  "success": true,
  "message": "Login successful",
  "user_id": "user-id-from-supabase",
  "access_token": "jwt-access-token"
}
```

**Response (Failure):**
```json
{
  "success": false,
  "message": "Invalid email or password",
  "user_id": null,
  "access_token": null
}
```

**Example Usage:**
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
     -H "Content-Type: application/json" \
     -d '{"email": "test@example.com", "password": "testpassword"}'
```

**Note:** Currently configured with test credentials for demonstration. For production use, set up proper Supabase credentials in your environment variables.

### Environment Variables

Required for Supabase authentication:
- `SUPABASE_URL`: Your Supabase project URL
- `SUPABASE_KEY`: Your Supabase anon/public key

## Development

The application uses:
- **FastAPI** - Modern Python web framework
- **Pydantic** - Data validation and settings
- **Uvicorn** - ASGI server
- **Supabase** - Authentication and database

### Running Tests

```bash
# Run all tests
python -m pytest

# Run specific test file
python -m pytest tests/routers/test_auth_router.py -v

# Run with coverage
python -m pytest --cov=src
```

## Project Structure

```
backend/
├── src/
│   ├── api/
│   │   └── v1/              # API version 1
│   ├── core/
│   │   ├── config.py        # Application configuration
│   │   └── database.py      # Database configuration
│   ├── routers/
│   │   ├── auth.py          # Authentication routes
│   │   ├── person.py        # Person-related routes
│   │   └── search.py        # Search routes
│   ├── schemas/
│   │   ├── auth.py          # Authentication schemas
│   │   └── ...              # Other schemas
│   ├── services/
│   │   ├── auth_service.py  # Authentication service
│   │   └── ...              # Other services
│   └── main.py              # FastAPI application
├── tests/
│   ├── routers/             # Router tests
│   ├── services/            # Service tests
│   └── ...                  # Other tests
├── main.py                  # Entry point
├── requirements.txt         # Dependencies
└── README.md
```

## API Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Security

- Authentication events are logged for debugging and monitoring
- Sensitive information (passwords, tokens) are not exposed in logs
- Supabase handles secure credential storage and validation
- Access tokens are provided for authenticated session management
