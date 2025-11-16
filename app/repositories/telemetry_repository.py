from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app import models, schemas

# return all telemetry from the database
def get_all_telemetry(db: Session):
    return db.query(models.Telemetry).all()

# return a telemetry by telemetry_id if it exists
def get_telemetry_by_telemetry_id(db: Session, telemetry_id: int):
    telemetry = db.query(models.Telemetry).filter(models.Telemetry.telemetry_id == telemetry_id).first()
    if not telemetry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Telemetry with telemetry_id='{telemetry_id}' is not found."
        )
    return telemetry

# create a new telemetry in the database (if telemetry_id doesn't already exist)
def create_telemetry(db: Session, telemetry: schemas.TelemetryCreate):
    telemetry_exists = db.query(models.Telemetry).filter(
        models.Telemetry.race_id == telemetry.race_id,
        models.Telemetry.session_id == telemetry.session_id,
        models.Telemetry.driver_number == telemetry.driver_number,
        models.Telemetry.telemetry_number == telemetry.telemetry_number
        ).first()
    if telemetry_exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=f"Telemetry with this telemetry_id='{telemetry.telemetry_id}' already exists."
            )
    
    db_telemetry = models.Telemetry(**telemetry.model_dump())
    db.add(db_telemetry)
    db.commit()
    db.refresh(db_telemetry)
    return db_telemetry

# update a telemetry
def update_telemetry(db: Session, telemetry_id: int, telemetry_update: schemas.TelemetryUpdate):
    telemetry_exists = db.query(models.Telemetry).filter(models.Telemetry.telemetry_id == telemetry_id).first()
    if not telemetry_exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Session with this telemetry_id='{telemetry_id}' is not found."
        )

    update_data = telemetry_update.model_dump()
    for field, value in update_data.items():
        if value is not None:
            setattr(telemetry_exists, field, value)

    db.commit()
    db.refresh(telemetry_exists)
    return telemetry_exists
    
# delete a telemetry
def delete_telemetry(db: Session, telemetry_id: int):
    telemetry_exists = db.query(models.Telemetry).filter(models.Telemetry.telemetry_id == telemetry_id).first()
    if not telemetry_exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Telemetry with this telemetry_id='{telemetry_id}' is not found."
        )
    db.delete(telemetry_exists)
    db.commit()
    return {"detail": f"Telemetry '{telemetry_id}' is deleted."}

