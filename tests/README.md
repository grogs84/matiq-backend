# Person Profile Test Suite

This document outlines the comprehensive test suite for the person profile and wrestler functionality.

## Test Structure

```
tests/
├── conftest.py                           # Shared fixtures and test configuration
├── test_person_profile.py                # Main API endpoint tests
├── services/
│   └── test_profile_service.py          # PersonService unit tests
├── schemas/
│   └── test_person_schemas.py           # Pydantic schema validation tests
└── integration/
    └── test_person_integration.py       # Full workflow integration tests
```

## Test Coverage

### 1. API Endpoint Tests (`test_person_profile.py`)
- ✅ GET `/api/v1/person/{slug}` - Person profile retrieval
- ✅ GET `/api/v1/person/{slug}/wrestler/stats` - Wrestler statistics
- ✅ GET `/api/v1/person/{slug}/wrestler/matches` - Wrestler match history
- ✅ Error handling (404 for non-existent persons)
- ✅ Query parameter validation (pagination, filtering)

### 2. Service Layer Tests (`test_profile_service.py`)
- ✅ `PersonService.get_person_by_slug()` - Database person lookup
- ✅ `PersonService.get_wrestler_stats()` - Wrestling statistics aggregation
- ✅ `PersonService.get_wrestler_matches()` - Match history with pagination
- ✅ Edge cases: missing persons, non-wrestlers, missing materialized view
- ✅ Query parameter handling (year filtering, pagination)

### 3. Schema Validation Tests (`test_person_schemas.py`)
- ✅ `PersonProfileResponse` - Person profile data structure
- ✅ `RoleResponse` - Role information validation
- ✅ `WrestlerStatsResponse` - Wrestling statistics structure
- ✅ `WrestlerMatchResult` - Individual match data validation
- ✅ `WrestlerMatchesResponse` - Paginated match results
- ✅ Error validation (invalid data types, missing fields)

### 4. Integration Tests (`test_person_integration.py`)
- ✅ Complete person profile workflow
- ✅ End-to-end wrestler stats retrieval
- ✅ Full match history with pagination
- ✅ Error handling across all endpoints
- ✅ Cross-service data consistency

## Test Fixtures

### Common Data Fixtures
- `sample_person_data` - Standard person information
- `sample_role_data` - Wrestler role data
- `sample_wrestler_stats` - Multi-year wrestling statistics
- `sample_wrestler_match` - Individual match details

### Database Fixtures
- `db_session` - Clean SQLite test database session
- `client` - FastAPI test client with dependency overrides

## Running Tests

### Run All Tests
```bash
./run_tests.sh
```

### Run Specific Test Categories
```bash
# Unit tests only
pytest tests/ -m "not integration" -v

# Integration tests only  
pytest tests/ -m integration -v

# Service tests only
pytest tests/services/ -v

# Schema validation tests
pytest tests/schemas/ -v
```

### Run Individual Test Files
```bash
pytest tests/test_person_profile.py -v
pytest tests/services/test_profile_service.py -v
pytest tests/schemas/test_person_schemas.py -v
pytest tests/integration/test_person_integration.py -v
```

## Test Scenarios Covered

### Happy Path
- ✅ Valid person lookup by slug
- ✅ Wrestler with statistics and matches
- ✅ Proper pagination and filtering
- ✅ Complete data serialization

### Error Cases
- ✅ Person not found (404 responses)
- ✅ Non-wrestler person requesting wrestler data
- ✅ Missing materialized view (graceful degradation)
- ✅ Invalid query parameters

### Edge Cases
- ✅ Person with no roles
- ✅ Wrestler with no match history
- ✅ Empty statistics results
- ✅ Large pagination requests

## Mocking Strategy

- **Database calls**: Mocked at the SQLAlchemy session level
- **External dependencies**: Dependency injection overrides
- **Complex queries**: Raw SQL execution mocked with realistic data
- **Materialized views**: Existence checks and data retrieval mocked

## Dependencies Required

```bash
pip install pytest pytest-asyncio httpx
```

## Test Data Patterns

All tests use consistent UUID patterns and realistic wrestling data:
- Person IDs: `550e8400-e29b-41d4-a716-446655440000`
- Role IDs: `660e8400-e29b-41d4-a716-446655440001`
- Slugs: `david-taylor`, `john-doe`
- Schools: Penn State, Ohio State
- Years: 2022, 2023
- Weight classes: 184, 197

This ensures tests are predictable and maintainable while covering real-world scenarios.
