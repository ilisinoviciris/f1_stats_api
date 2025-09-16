from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from .. import models, schemas
import httpx

# return all drivers from the database
def get_all_drivers(db: Session):
    return db.query(models.Driver).all()

# return a driver by driver_id if it exists
def get_driver_by_driver_id(db: Session, driver_id: str):
    driver = db.query(models.Driver).filter(models.Driver.driver_id == driver_id).first()
    if not driver:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Driver with driver_id='{driver_id}' is not found."
        )
    return driver

# create a new driver in the database (if driver_id doesn't already exist)
def create_driver(db: Session, driver: schemas.DriverCreate):
    driver_exists = db.query(models.Driver).filter(models.Driver.driver_id == driver.driver_id).first()
    if driver_exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=f"Driver with this driver_id='{driver.driver_id}' already exists."
            )
    
    db_driver = models.Driver(**driver.model_dump())
    db.add(db_driver)
    db.commit()
    db.refresh(db_driver)
    return db_driver

# update a driver
def update_driver(db: Session, driver_id: str, driver_update: schemas.DriverUpdate):
    driver_exists = db.query(models.Driver).filter(models.Driver.driver_id == driver_id).first()
    if not driver_exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Driver with this driver_id='{driver_id}' is not found."
        )

    update_data = driver_update.model_dump()
    for field, value in update_data.items():
        if value is not None:
            setattr(driver_exists, field, value)

    db.commit()
    db.refresh(driver_exists)
    return driver_exists
    
# delete a driver
def delete_driver(db: Session, driver_id: str):
    driver_exists = db.query(models.Driver).filter(models.Driver.driver_id == driver_id).first()
    if not driver_exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Driver with this driver_id='{driver_id}' is not found."
        )
    db.delete(driver_exists)
    db.commit()
    return {"detail": f"Driver '{driver_id}' is deleted."}

