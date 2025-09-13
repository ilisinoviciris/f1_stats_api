from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from .. import models, schemas

# return all drivers from the database
def get_all_drivers(db: Session):
    return db.query(models.Driver).all()

# return driver by driver_id if it exists
def get_driver_by_driver_id(db: Session, driver_id: str):
    return db.query(models.Driver).filter(models.Driver.driver_id == driver_id).first()

# create new driver in the database (if driver_id doesn't already exist)
def create_driver(db: Session, driver: schemas.DriverCreate):
    driver_exists = get_driver_by_driver_id(db, driver.driver_id)
    if driver_exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Driver with this driver_id already exists"
            )
    
    db_driver = models.Driver(
        driver_id = driver.driver_id,
        first_name = driver.first_name,
        last_name = driver.last_name,
        driver_number = driver.driver_number,
        name_acronym = driver.name_acronym,
        team_name = driver.team_name
    )

    db.add(db_driver)
    db.commit()
    db.refresh(db_driver)
    return db_driver



