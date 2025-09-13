from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from .. import schemas, database
from app.repositories import driver_repository

# initializing router 
router = APIRouter(prefix="/drivers", tags=["Drivers"])

# dependency for the database
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# endpoint for fetching all drivers -> GET /drivers
@router.get("/", response_model=list[schemas.Driver])
def get_all_drivers(db: Session = Depends(get_db)):
    try:
        return driver_repository.get_all_drivers(db=db)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {str(e)}"
        )

# endpoint for fetching a driver by id -> GET /drivers/{driver_id}
@router.get("/{driver_id}", response_model=schemas.Driver)
def get_driver(driver_id: str, db: Session = Depends(get_db)):
    driver = driver_repository.get_driver_by_driver_id(db=db, driver_id=driver_id)
    if not driver:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Driver with driver_id={driver_id} is not found."
        )
    return driver

# enpoint for creating a new driver -> POST /drivers
@router.post("/", response_model=schemas.Driver)
def create_driver(driver: schemas.DriverCreate, db: Session = Depends(get_db)):
    try:
        return driver_repository.create_driver(db=db, driver=driver)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {str(e)}"
        )







