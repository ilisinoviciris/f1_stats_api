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

# test: create a driver
def test_create_driver():
    response = client.post("/drivers/", json={
        "driver_id": "test_driver",
        "full_name": "Test DRIVER",
        "first_name": "Test",
        "last_name": "Driver",
        "driver_number": 38,
        "name_acronym": "TES",
        "team_name": "Test Team",
        "country_code": "TST"
    })
    # checking if it's code HTTP 201 Created
    assert response.status_code == 201
    data = response.json()
    assert data["driver_id"] == "test_driver"
    assert data["team_name"] == "Test Team"

# test: get all drivers
def test_get_all_drivers():
    response = client.get("/drivers/")
    # checking if it's code HTTP 200 OK
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0

# test: get driver by driver id
def test_get_driver_by_driver_id():
    response = client.get("/drivers/test_driver")
    # checking if it's code HTTP 200 OK
    assert response.status_code == 200
    data = response.json()
    assert data["driver_id"] == "test_driver"

#test: update a driver
def test_update_driver():
    response = client.put("/drivers/test_driver", json={
        "driver_number": 20,
        "team_name": "New Team"
    })
    # checking if it's code HTTP 200 OK
    assert response.status_code == 200
    data = response.json()
    assert data["driver_number"] == 20
    assert data["team_name"] == "New Team"

# test: delete a driver
def test_delete_driver():
    response = client.delete("/drivers/test_driver")
    # checking if it's code HTTP 200 OK
    assert response.status_code == 200
    data = response.json()
    assert data["detail"] == "Driver 'test_driver' is deleted."

