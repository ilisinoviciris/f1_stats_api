from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app import models, schemas, database
from app.repositories import lap_repository
import httpx

# initializing router 
router = APIRouter(prefix="/laps", tags=["Laps"])

OPENF1_LAPS_URL = "https://api.openf1.org/v1/laps"

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

# fetch all laps by race_id from OpenF1 API and save/update them in the database -> POST /laps/sync/{race_id}
# returns count of created and updated laps
@router.post("/sync/{race_id}")
def fetch_laps(race_id: int, db: Session = Depends(get_db)):
    try:
        response = httpx.get(OPENF1_LAPS_URL, params={"meeting_key": race_id}, timeout=10)
        response.raise_for_status()
        laps_json = response.json()
    except httpx.HTTPError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Error retrieving laps from OpenF1 API: {str(e)}"
        )
    
    if not isinstance(laps_json, list) or len(laps_json) == 0:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"OpenF1 API returned an invalid or empty response."
        )

    created = 0
    updated = 0

    for l in laps_json:
        lap_data = schemas.LapCreate(
            race_id = race_id,
            session_id = l.get("session_key"),
            driver_number = l.get("driver_number"),
            lap_number = l.get("lap_number"),
            lap_duration = l.get("lap_duration", 0),
            duration_sector_1 = l.get("duration_sector_1", 0),
            duration_sector_2 = l.get("duration_sector_2", 0),
            duration_sector_3 = l.get("duration_sector_3", 0),
            i1_speed = l.get("i1_speed", 0),
            i2_speed = l.get("i2_speed", 0),
            st_speed = l.get("st_speed", 0),
            is_pit_out_lap = l.get("is_pit_out_lap", False)
        ) 

        lap_exists = db.query(models.Lap).filter(
            models.Lap.race_id == race_id,
            models.Lap.session_id == lap_data.session_id,
            models.Lap.driver_number == lap_data.driver_number,
            models.Lap.lap_number == lap_data.lap_number
            ).first()
        
        if lap_exists:
            update_data = lap_data.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                if value is not None:
                    setattr(lap_exists, field, value)
            db.commit()
            db.refresh(lap_exists)
            updated += 1
        else:
            lap_repository.create_session(db, lap_data)
            created += 1
        
    return {"created": created, "updated": updated, "total": len(laps_json)}