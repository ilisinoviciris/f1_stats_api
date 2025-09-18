from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app import models, schemas, database
from app.repositories import race_repository
import httpx

# initializing router 
router = APIRouter(prefix="/races", tags=["Races"])

OPENF1_MEETINGS_URL = "https://api.openf1.org/v1/meetings"

# dependency for the database
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# endpoint for retrieving all races -> GET /races/
@router.get("/", response_model=List[schemas.Race])
def get_all_races(db: Session = Depends(get_db)):
    return race_repository.get_all_races(db)

# endpoint for retrieving a race by race_id -> GET /races/{race_id}
@router.get("/{race_id}", response_model=schemas.Race)
def get_race(race_id: int, db: Session = Depends(get_db)):
    return race_repository.get_race_by_race_id(db, race_id)

# endpoint for creating a new race -> POST /races/
@router.post("/", response_model=schemas.Race, status_code=201)
def create_race(race: schemas.RaceCreate, db: Session = Depends(get_db)):
    return race_repository.create_race(db, race)

# endpoint for updating a race -> PUT /races/{race_id}
@router.put("/{race_id}", response_model=schemas.Race)
def update_race(race_id: int, race: schemas.RaceUpdate, db: Session = Depends(get_db)):
    return race_repository.update_race(db, race_id, race)

# endpoint for deleting a race -> DELETE /races/{race_id}
@router.delete("/{race_id}")
def delete_race(race_id: int, db: Session = Depends(get_db)):
    return race_repository.delete_race(db, race_id)

# fetch races from OpenF1 API and save/update them in the database
# returns count of created and updated races
@router.post("/sync")
def fetch_races(db: Session = Depends(get_db)):
    try:
        response = httpx.get(OPENF1_MEETINGS_URL, timeout=10)
        response.raise_for_status()
        races_json = response.json()
    except httpx.HTTPError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Error retrieving races from OpenF1 API: {str(e)}"
        )
    
    if not isinstance(races_json, list) or len(races_json) == 0:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"OpenF1 API returned an invalid or empty response."
        )

    created = 0
    updated = 0

    for r in races_json:
        race_id = r.get("meeting_key")
        race_name = r.get("meeting_name")
        circuit_name = r.get("circuit_short_name")
        location = r.get("location")
        country_name = r.get("country_name")
        year = r.get("year")

        race_data = schemas.RaceCreate(
            race_id = race_id,
            race_name = race_name,
            circuit_name = circuit_name,
            location = location,
            country_name = country_name,
            year = year  
        )

        race_exists = db.query(models.Race).filter(models.Race.race_id == race_id).first()
        
        if race_exists:
            update_data = race_data.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                if value is not None:
                    setattr(race_exists, field, value)
            db.commit()
            db.refresh(race_exists)
            updated += 1
        else:
            race_repository.create_race(db, race_data)
            created += 1
        
    return {"created": created, "updated": updated, "total": len(races_json)}


