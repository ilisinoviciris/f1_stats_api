from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app import models, schemas, database
from app.repositories import driver_repository
import httpx
from app.utils import normalize_driver_id

# initializing router 
router = APIRouter(prefix="/drivers", tags=["Drivers"])

OPENF1_DRIVERS_URL = "https://api.openf1.org/v1/drivers"

# dependency for the database
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# endpoint for retrieving all drivers -> GET /drivers/
@router.get("/", response_model=List[schemas.Driver])
def get_all_drivers(db: Session = Depends(get_db)):
    try:
        return driver_repository.get_all_drivers(db)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {str(e)}"
        )

# endpoint for retrieving a driver by driver_id -> GET /drivers/{driver_id}
@router.get("/{driver_id}", response_model=schemas.Driver)
def get_driver(driver_id: str, db: Session = Depends(get_db)):
    try:
        return driver_repository.get_driver_by_driver_id(db, driver_id)
    except httpx.HTTPError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {str(e)}" 
        )

# endpoint for creating a new driver -> POST /drivers/
@router.post("/", response_model=schemas.Driver, status_code=201)
def create_driver(driver: schemas.DriverCreate, db: Session = Depends(get_db)):
    try:
        if not driver.driver_id:
            driver.driver_id = normalize_driver_id(driver.full_name)
        return driver_repository.create_driver(db, driver)
    except httpx.HTTPError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {str(e)}" 
        )
    
# endpoint for updating a driver -> PUT /drivers/{driver_id}
@router.put("/{driver_id}", response_model=schemas.Driver)
def update_driver(driver_id: str, driver: schemas.DriverUpdate, db: Session = Depends(get_db)):
    try:
        return driver_repository.update_driver(db, driver_id, driver)
    except httpx.HTTPError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {str(e)}" 
        )
    
# endpoint for deleting a driver -> DELETE /drivers/{driver_id}
@router.delete("/{driver_id}")
def delete_driver(driver_id: str, db: Session = Depends(get_db)):
    try:
        return driver_repository.delete_driver(db, driver_id)
    except httpx.HTTPError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {str(e)}" 
        )


# fetch drivers from OpenF1 API and save/update them in the database
# returns count of created and updated drivers
@router.post("/sync")
def fetch_drivers(db: Session = Depends(get_db)):
    try:
        response = httpx.get(OPENF1_DRIVERS_URL)
        response.raise_for_status()
        drivers_json = response.json()
    except httpx.HTTPError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Error retrieving drivers from OpenF1: {str(e)}"    
        )
    created = 0
    updated = 0

    for d in drivers_json:
        full_name = d.get("full_name", "")
        driver_id = normalize_driver_id(full_name)

        country_code = d.get("country_code")
        if not country_code:
            for entry in drivers_json:
                if normalize_driver_id(entry.get("full_name")) == driver_id and entry.get("country_code"):
                    country_code = entry.get("country_code")
                    break

        if not country_code:
            country_code = ""       

        driver_data = schemas.DriverCreate(
            driver_id = driver_id,
            full_name = full_name,
            first_name = d.get("first_name") or "",
            last_name = d.get("last_name") or "",
            driver_number = d.get("driver_number", 0),
            name_acronym = d.get("name_acronym") or "",
            team_name = d.get("team_name") or "",
            country_code = country_code      
        )


        driver_exists = db.query(models.Driver).filter(models.Driver.driver_id == driver_id).first()
        
        if driver_exists:
            update_data = driver_data.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                if value is not None:
                    setattr(driver_exists, field, value)
            db.commit()
            db.refresh(driver_exists)
            updated += 1
        else:
            driver_repository.create_driver(db, driver_data)
            created += 1
        
    return {"created": created, "updated": updated, "total": len(drivers_json)}


