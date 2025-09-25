import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import Base, engine, SessionLocal
from app import models
import random

# create a new test client
client = TestClient(app)

created_stint_id = None
random_driver_number = random.randint(99, 199)

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

# test: create a stint
def test_create_stint():
    global created_stint_id, random_driver_number

    response = client.post("/stints/", json={ 
        "race_id": 9999,
        "session_id": 8888,
        "driver_number": random_driver_number,
        "stint_number": 1,
        "lap_start": 1,
        "lap_end": 5,
        "tyre_compound": "MEDIUM"
    })
    # checking if it's code HTTP 201 Created
    assert response.status_code == 201
    data = response.json()
    created_stint_id = data["stint_id"]
    assert data["race_id"] == 9999
    assert data["tyre_compound"] == "MEDIUM"

# test: get all stints
def test_get_all_stints():
    assert created_stint_id is not None
    response = client.get("/stints/")
    # checking if it's code HTTP 200 OK
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0

# test: get stint by stint id
def test_get_stint_by_stint_id():
    assert created_stint_id is not None
    response = client.get(f"/stints/{created_stint_id}")
    # checking if it's code HTTP 200 OK
    assert response.status_code == 200
    data = response.json()
    assert data["stint_id"] == created_stint_id
    assert data["stint_number"] == 1

#test: update a stint
def test_update_stint():
    assert created_stint_id is not None
    response = client.put(f"/stints/{created_stint_id}", json={
        "lap_start": 1,
        "tyre_compound": "SOFT"
    })
    # checking if it's code HTTP 200 OK
    assert response.status_code == 200
    data = response.json()
    assert data["lap_start"] == 1
    assert data["tyre_compound"] == "SOFT"

# test: delete a stint
def test_delete_stint():
    assert created_stint_id is not None
    response = client.delete(f"/stints/{created_stint_id}")
    # checking if it's code HTTP 200 OK
    assert response.status_code == 200
    data = response.json()
    assert data["detail"] == f"Stint '{created_stint_id}' is deleted."

