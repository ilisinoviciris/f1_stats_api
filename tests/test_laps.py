import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import Base, engine, SessionLocal
import random

# create a new test client
client = TestClient(app)

created_lap_id = None
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

# test: create a lap
def test_create_lap():
    global created_lap_id, random_driver_number

    response = client.post("/laps/", json={
        "race_id": 12345,
        "session_id": 56789,
        "driver_number": random_driver_number,
        "lap_number": 1,
        "lap_duration": 90.000,
        "duration_sector_1": 20.000,
        "duration_sector_2": 50.000,
        "duration_sector_3": 30.000,
        "i1_speed": 200.0,
        "i2_speed": 210.0,
        "st_speed": 300.0,
        "is_pit_out_lap": False
    })
    # checking if it's code HTTP 201 Created
    assert response.status_code == 201
    data = response.json()
    created_lap_id = data["lap_id"]
    assert data["driver_number"] == random_driver_number
    assert data["lap_number"] == 1

# test: get all laps
def test_get_all_laps():
    assert created_lap_id is not None
    response = client.get("/laps/")
    # checking if it's code HTTP 200 OK
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0

# test: get lap by lap id
def test_get_lap_by_lap_id():
    assert created_lap_id is not None
    response = client.get(f"/laps/{created_lap_id}")
    # checking if it's code HTTP 200 OK
    assert response.status_code == 200
    data = response.json()
    assert data["lap_id"] == created_lap_id
    assert data["driver_number"] == random_driver_number

#test: update a lap
def test_update_lap():
    assert created_lap_id is not None
    response = client.put(f"/laps/{created_lap_id}", json={
        "lap_duration": 95.236,
        "is_pit_out_lap": True
    })
    # checking if it's code HTTP 200 OK
    assert response.status_code == 200
    data = response.json()
    assert data["lap_duration"] == 95.236
    assert data["is_pit_out_lap"] is True

# test: delete a lap
def test_delete_lap(): 
    assert created_lap_id is not None
    response = client.delete(f"/laps/{created_lap_id}")
    # checking if it's code HTTP 200 OK
    assert response.status_code == 200
    data = response.json()
    assert data["detail"] == f"Lap '{created_lap_id}' is deleted."