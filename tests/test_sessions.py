import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import Base, engine, SessionLocal
import random

# create a new test client
client = TestClient(app)

created_id = None
random_session_id = random.randint(10000, 99999)

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

# test: create a session
def test_create_session():
    global created_id, random_session_id
    response = client.post("/sessions/", json={
        "session_id": random_session_id,
        "race_id": 54321,
        "session_name": "Test Session",
        "session_type": "Qualifying"
    })
    # checking if it's code HTTP 201 Created
    assert response.status_code == 201
    data = response.json()
    assert data["session_id"] == random_session_id
    assert data["session_type"] == "Qualifying"
    assert "id" in data
    global created_id
    created_id = data["id"]

# test: get all sessions
def test_get_all_sessions():
    assert created_id is not None
    response = client.get("/sessions/")
    # checking if it's code HTTP 200 OK
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0

# test: get session by id
def test_get_session_by_id():
    assert created_id is not None
    response = client.get(f"/sessions/{created_id}")
    # checking if it's code HTTP 200 OK
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == created_id
    assert data["session_id"] == random_session_id
    assert data["race_id"] == 54321
    assert data["session_name"] == "Test Session"
    assert data["session_type"] == "Qualifying"

#test: update a session
def test_update_session():
    assert created_id is not None
    response = client.put(f"/sessions/{created_id}", json={
        "session_name": "Practice 3 Updated"
    })
    # checking if it's code HTTP 200 OK
    assert response.status_code == 200
    data = response.json()
    assert data["session_name"] == "Practice 3 Updated"

# test: delete a session
def test_delete_session(): 
    assert created_id is not None
    response = client.delete(f"/sessions/{created_id}")
    # checking if it's code HTTP 200 OK
    assert response.status_code == 200
    data = response.json()
    assert data["detail"] == f"Session '{created_id}' is deleted."