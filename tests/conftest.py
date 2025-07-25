import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from datetime import date

from src.main import app
from src.core.database import get_db, Base

# Use in-memory SQLite for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture
def db_session():
    """Create a fresh database session for each test."""
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        # Drop all tables after test
        Base.metadata.drop_all(bind=engine)

@pytest.fixture
def test_app(db_session):
    """Create FastAPI app for testing with test database."""
    app.dependency_overrides[get_db] = lambda: db_session
    yield app
    app.dependency_overrides.clear()

@pytest.fixture
def client(test_app):
    """Create a test client for the FastAPI app."""
    return TestClient(test_app)

@pytest.fixture
def test_client(test_app):
    """Create a test client for the FastAPI app."""
    return TestClient(test_app)

@pytest.fixture
def sample_data(db_session):
    """Create sample test data."""
    from src.models import Person, Role, School, Tournament, Participant
    
    # Create sample persons
    person1 = Person(
        person_id="1",
        first_name="David",
        last_name="Taylor",
        search_name="David Taylor",
        state_of_origin="PA"
    )
    person2 = Person(
        person_id="2", 
        first_name="Jordan",
        last_name="Burroughs",
        search_name="Jordan Burroughs",
        state_of_origin="NJ"
    )
    
    # Create sample schools
    school1 = School(
        school_id="1",
        name="Penn State",
        location="University Park, PA",
        school_type="University"
    )
    school2 = School(
        school_id="2",
        name="Iowa State",
        location="Ames, IA", 
        school_type="University"
    )
    
    # Create sample tournaments
    tournament1 = Tournament(
        tournament_id="1",
        name="NCAA Championships",
        date=date(2023, 3, 16),
        year=2023,
        location="Tulsa, OK"
    )
    
    # Create sample roles
    role1 = Role(role_id="1", person_id="1", role_type="wrestler")
    role2 = Role(role_id="2", person_id="2", role_type="wrestler")
    
    # Create sample participants
    participant1 = Participant(
        participant_id="1",
        role_id="1",
        school_id="1",
        tournament_id="1",
        person_id="1",
        year=2023,
        weight_class="165"
    )
    participant2 = Participant(
        participant_id="2",
        role_id="2", 
        school_id="2",
        tournament_id="1",
        person_id="2",
        year=2023,
        weight_class="174"
    )
    
    # Add all to session
    db_session.add_all([
        person1, person2, school1, school2, tournament1,
        role1, role2, participant1, participant2
    ])
    db_session.commit()
    
    return {
        "persons": [person1, person2],
        "schools": [school1, school2],
        "tournaments": [tournament1],
        "roles": [role1, role2],
        "participants": [participant1, participant2]
    }
