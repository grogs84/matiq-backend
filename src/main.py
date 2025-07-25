#      description="API for MatIQ, a wrestling analytics platform",
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.orm import Session

from .api import api_router
from .core.config import settings
from .core.database import get_db
from .models.person import Person

app = FastAPI(
    title="MatIQ API",
    description="API for MatIQ, a wrestling analytics platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

print(f"DATABASE_URL: {settings.DATABASE_URL}")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix="/api/v1")


@app.get("/")
def read_root():
    """Root endpoint"""
    return {"message": "Welcome to Matiq API"}


@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    """Health check endpoint"""
    try:
        # Perform a simple query to check database connection
        db.execute(text("SELECT 1"))
        return {"status": "healthy"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}


# this is a test endpoint to check if the person table exists and can be queried
# for dev only, not for production use
@app.get("/person_test")
def test_person(db: Session = Depends(get_db)):
    """Test endpoint for person"""
    try:

        count = db.query(Person).count()

        person = db.query(Person).limit(5).all()

        return {
            "status": "success",
            "person_count": count,
            "persons": [
                {
                    "person_id": p.person_id,
                    "first_name": p.first_name,
                    "last_name": p.last_name,
                }
                for p in person
            ],
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}
