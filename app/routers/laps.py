from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app import models, schemas, database
from app.repositories import lap_repository
import httpx

# initializing router 
router = APIRouter(prefix="/laps", tags=["Laps"])

# dependency for the database
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# endpoint for retrieving all laps -> GET /laps/
@router.get("/", response_model=List[schemas.Lap])
def get_all_laps(db: Session = Depends(get_db)):
    return lap_repository.get_all_laps(db)

# endpoint for retrieving a lap by lap_id -> GET /laps/{lap_id}
@router.get("/{lap_id}", response_model=schemas.Lap)
def get_lap(lap_id: int, db: Session = Depends(get_db)):
    return lap_repository.get_lap_by_lap_id(db, lap_id)

# endpoint for creating a new lap -> POST /laps/
@router.post("/", response_model=schemas.Lap, status_code=201)
def create_lap(lap: schemas.LapCreate, db: Session = Depends(get_db)):
    return lap_repository.create_lap(db, lap)

# endpoint for updating a lap -> PUT /laps/{lap_id}
@router.put("/{lap_id}", response_model=schemas.Lap)
def update_lap(lap_id: int, lap: schemas.LapUpdate, db: Session = Depends(get_db)):
    return lap_repository.update_lap(db, lap_id, lap)

# endpoint for deleting a lap -> DELETE /laps/{lap_id}
@router.delete("/{lap_id}")
def delete_lap(lap_id: int, db: Session = Depends(get_db)):
    return lap_repository.delete_lap(db, lap_id)

