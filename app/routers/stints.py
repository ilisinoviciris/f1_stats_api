from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app import models, schemas, database
from app.repositories import stint_repository
import httpx

# initializing router 
router = APIRouter(prefix="/stints", tags=["Stints"])

OPENF1_STINTS_URL = "https://api.openf1.org/v1/stints"

# dependency for the database
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# endpoint for retrieving all stints -> GET /stints/
@router.get("/", response_model=List[schemas.Stint])
def get_all_stints(db: Session = Depends(get_db)):
    return stint_repository.get_all_stints(db)

# endpoint for retrieving a stint by stint_id -> GET /stints/{id}
@router.get("/{stint_id}", response_model=schemas.Stint)
def get_stint_by_id(stint_id: int, db: Session = Depends(get_db)):
    return stint_repository.get_stint_by_stint_id(db, stint_id)

# endpoint for creating a new stint -> POST /stints/
@router.post("/", response_model=schemas.Stint, status_code=201)
def create_stint(stint: schemas.StintCreate, db: Session = Depends(get_db)):
    return stint_repository.create_stint(db, stint)

# endpoint for updating a stint -> PUT /stints/{id}
@router.put("/{stint_id}", response_model=schemas.Stint)
def update_stint(stint_id: int, stint: schemas.StintUpdate, db: Session = Depends(get_db)):
    return stint_repository.update_stint(db, stint_id, stint)

# endpoint for deleting a stint -> DELETE /stints/{id}
@router.delete("/{stint_id}")
def delete_stint(stint_id: int, db: Session = Depends(get_db)):
    return stint_repository.delete_stint(db, stint_id)

# fetch all stints by race_id from OpenF1 API and save/update them in the database -> POST /stints/sync/{race_id}
# returns count of created and updated stints
@router.post("/sync/{race_id}")
def fetch_stints(race_id: int, db: Session = Depends(get_db)):
    try:
        response = httpx.get(OPENF1_STINTS_URL, params={"meeting_key": race_id}, timeout=10)
        response.raise_for_status()
        stints_json = response.json()
    except httpx.HTTPError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Error retrieving stints from OpenF1 API: {str(e)}"
        )
    
    if not isinstance(stints_json, list) or len(stints_json) == 0:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"OpenF1 API returned an invalid or empty response."
        )

    created = 0
    updated = 0

    for s in stints_json:
        race_id = race_id
        session_id = s.get("session_key")
        driver_number = s.get("driver_number")
        stint_number = s.get("stint_number")
        lap_start = s.get("lap_start")
        lap_end = s.get("lap_end")
        tyre_compound = s.get("compound")
        tyre_age_at_start = s.get("tyre_age_at_start")

        stint_data = schemas.StintCreate(
            race_id = race_id,
            session_id = session_id,
            driver_number = driver_number,
            stint_number = stint_number,
            lap_start = lap_start,
            lap_end = lap_end,
            tyre_compound = tyre_compound,
            tyre_age_at_start = tyre_age_at_start
        )

        stint_exists = db.query(models.Stint).filter(
            models.Stint.race_id == stint_data.race_id,
            models.Stint.session_id == stint_data.session_id,
            models.Stint.driver_number == stint_data.driver_number,
            models.Stint.stint_number == stint_data.stint_number
        ).first()
        
        if stint_exists:
            update_data = stint_data.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                if value is not None:
                    setattr(stint_exists, field, value)
            db.commit()
            db.refresh(stint_exists)
            updated += 1
        else:
            stint_repository.create_stint(db, stint_data)
            created += 1
        
    return {"created": created, "updated": updated, "total": len(stints_json)}


