#      description="API for MatIQ, a wrestling analytics platform",
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text
from .core.config import settings
from .core.database import get_db
from .api import api_router


app = FastAPI(
    title="MatIQ API",
    description="API for MatIQ, a wrestling analytics platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
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
        # First check if table exists
        table_check = db.execute(text("SELECT to_regclass('person')"))
        table_exists = table_check.fetchone()[0] is not None
        
        if not table_exists:
            return {"status": "error", "error": "Table 'person' does not exist"}
        
        # Then query the data
        result = db.execute(text("SELECT p.person_id, p.search_name from person p limit 10"))
        persons = result.fetchall()
        
        return {
            "status": "success",
            "table_exists": table_exists,
            "count": len(persons),
            "person_ids": [row[0] for row in persons],
            "search_names": [row[1] for row in persons]
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}