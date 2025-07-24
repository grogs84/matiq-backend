# Matiq Backend

A modern FastAPI backend application.

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

3. Run the application:
```bash
python main.py
```

The API will be available at:
- http://localhost:8000 - API root
- http://localhost:8000/docs - Interactive API documentation
- http://localhost:8000/health - Health check endpoint

## Development

The application uses:
- **FastAPI** - Modern Python web framework
- **Pydantic** - Data validation and settings
- **Uvicorn** - ASGI server

## Project Structure

```
backend/
├── src/
│   ├── core/
│   │   ├── __init__.py
│   │   └── config.py      # Application configuration
│   ├── __init__.py
│   └── main.py            # FastAPI application
├── main.py                # Entry point
├── requirements.txt       # Dependencies
└── README.md
```

## API Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
