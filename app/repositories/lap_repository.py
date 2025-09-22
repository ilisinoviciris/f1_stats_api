from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app import models, schemas

# return all laps from the database
def get_all_laps(db: Session):
    return db.query(models.Lap).all()

# return a lap by lap_id if it exists
def get_lap_by_lap_id(db: Session, lap_id: int):
    lap = db.query(models.Lap).filter(models.Lap.lap_id == lap_id).first()
    if not lap:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Lap with lap_id='{lap_id}' is not found."
        )
    return lap

# helper: check if lap exists by unique keys
def lap_exists(db: Session, lap:schemas.LapCreate):
    return db.query(models.Lap).filter(
        models.Lap.race_id == lap.race_id,
        models.Lap.session_id == lap.session_id,
        models.Lap.driver_number == lap.driver_number,
        models.Lap.lap_number == lap.lap_number
    ).first()

# create a new lap in the database 
def create_lap(db: Session, lap: schemas.LapCreate):
    lap_exists = db.query(models.Lap).filter(
        models.Lap.race_id == lap.race_id,
        models.Lap.session_id == lap.session_id,
        models.Lap.driver_number == lap.driver_number,
        models.Lap.lap_number == lap.lap_number
    ).first()

    if lap_exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=f"Lap already exists."
            )

    db_lap = models.Lap(**lap.model_dump())
    db.add(db_lap)
    db.commit()
    db.refresh(db_lap)
    return db_lap

# update a lap
def update_lap(db: Session, lap_id: int, lap_update: schemas.LapUpdate):
    lap_exists = db.query(models.Lap).filter(models.Lap.lap_id == lap_id).first()
    if not lap_exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Lap with this lap_id='{lap_id}' is not found."
        )

    update_data = lap_update.model_dump()
    for field, value in update_data.items():
        if value is not None:
            setattr(lap_exists, field, value)

    db.commit()
    db.refresh(lap_exists)
    return lap_exists
    
# delete a lap
def delete_lap(db: Session, lap_id: int):
    lap_exists = db.query(models.Lap).filter(models.Lap.lap_id == lap_id).first()
    if not lap_exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Lap with this lap_id='{lap_id}' is not found."
        )
    db.delete(lap_exists)
    db.commit()
    return {"detail": f"Lap '{lap_id}' is deleted."}

