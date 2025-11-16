from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app import models, schemas, database
from app.repositories import telemetry_repository
import httpx

# initializing router 
router = APIRouter(prefix="/telemetry", tags=["Telemetry"])

# dependency for the database
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# endpoint for retrieving all telemetry data -> GET /telemetry/
@router.get("/", response_model=List[schemas.Telemetry])
def get_all_telemetry(db: Session = Depends(get_db)):
    return telemetry_repository.get_all_telemetry(db)

# endpoint for retrieving a telemetry by telemetry_id -> GET /telemetry/{id}
@router.get("/{telemetry_id}", response_model=schemas.Telemetry)
def get_telemetry_by_id(telemetry_id: int, db: Session = Depends(get_db)):
    return telemetry_repository.get_telemetry_by_telemetry_id(db, telemetry_id)

# endpoint for creating a new telemetry -> POST /telemetry/
@router.post("/", response_model=schemas.Telemetry, status_code=201)
def create_telemetry(telemetry: schemas.TelemetryCreate, db: Session = Depends(get_db)):
    return telemetry_repository.create_telemetry(db, telemetry)

# endpoint for updating a telemetry -> PUT /telemetry/{id}
@router.put("/{telemetry_id}", response_model=schemas.Telemetry)
def update_telemetry(telemetry_id: int, telemetry: schemas.TelemetryUpdate, db: Session = Depends(get_db)):
    return telemetry_repository.update_telemetry(db, telemetry_id, telemetry)

# endpoint for deleting a telemetry -> DELETE /telemetry/{id}
@router.delete("/{telemetry_id}")
def delete_telemetry(telemetry_id: int, db: Session = Depends(get_db)):
    return telemetry_repository.delete_telemetry(db, telemetry_id)

