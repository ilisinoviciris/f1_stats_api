import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import Base, engine, SessionLocal
from app import models

# create a new test client
client = TestClient(app)

# create a fresh test database before each test session
@pytest.fixture(scope="module", autouse=True)
def setup_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield  

# dependency override (isolated session for tests)
def override_get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides = {}
app.dependency_overrides[lambda: next(override_get_db())] = override_get_db

# test: create a race
def test_create_race():
    response = client.post("/races/", json={
        "race_id": 9999,
        "race_name": "Test Name",
        "circuit_name": "Test",
        "location": "Test City",
        "country_name": "Test Country",
        "year": 2025
    })
    # checking if it's code HTTP 201 Created
    assert response.status_code == 201
    data = response.json()
    assert data["race_id"] == 9999
    assert data["race_name"] == "Test Name"

# test: get all races
def test_get_all_races():
    response = client.get("/races/")
    # checking if it's code HTTP 200 OK
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0

# test: get race by race id
def test_get_race_by_race_id():
    response = client.get("/races/9999")
    # checking if it's code HTTP 200 OK
    assert response.status_code == 200
    data = response.json()
    assert data["race_id"] == 9999

#test: update a race
def test_update_race():
    response = client.put("/races/9999", json={
        "circuit_name": "New Circuit",
        "year": 2024
    })
    # checking if it's code HTTP 200 OK
    assert response.status_code == 200
    data = response.json()
    assert data["circuit_name"] == "New Circuit"
    assert data["year"] == 2024

# test: delete a race
def test_delete_race():
    response = client.delete("/races/9999")
    # checking if it's code HTTP 200 OK
    assert response.status_code == 200
    data = response.json()
    assert data["detail"] == "Race '9999' is deleted."

