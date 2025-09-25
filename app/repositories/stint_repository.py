from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app import models, schemas

# return all stints from the database
def get_all_stints(db: Session):
    return db.query(models.Stint).all()

# return a stint by stint_id if it exists
def get_stint_by_stint_id(db: Session, stint_id: int):
    stint = db.query(models.Stint).filter(models.Stint.stint_id == stint_id).first()
    if not stint:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Stint with stint_id='{stint_id}' is not found."
        )
    return stint

# create a new stint in the database (if stint_id doesn't already exist)
def create_stint(db: Session, stint: schemas.StintCreate):
    stint_exists = db.query(models.Stint).filter(
        models.Stint.race_id == stint.race_id,
        models.Stint.session_id == stint.session_id,
        models.Stint.driver_number == stint.driver_number,
        models.Stint.stint_number == stint.stint_number
        ).first()
    if stint_exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=f"Stint with this stint_id='{stint.stint_id}' already exists."
            )
    
    db_stint = models.Stint(**stint.model_dump())
    db.add(db_stint)
    db.commit()
    db.refresh(db_stint)
    return db_stint

# update a stint
def update_stint(db: Session, stint_id: int, stint_update: schemas.StintUpdate):
    stint_exists = db.query(models.Stint).filter(models.Stint.stint_id == stint_id).first()
    if not stint_exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Session with this stint_id='{stint_id}' is not found."
        )

    update_data = stint_update.model_dump()
    for field, value in update_data.items():
        if value is not None:
            setattr(stint_exists, field, value)

    db.commit()
    db.refresh(stint_exists)
    return stint_exists
    
# delete a stint
def delete_stint(db: Session, stint_id: int):
    stint_exists = db.query(models.Stint).filter(models.Stint.stint_id == stint_id).first()
    if not stint_exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Stint with this stint_id='{stint_id}' is not found."
        )
    db.delete(stint_exists)
    db.commit()
    return {"detail": f"Stint '{stint_id}' is deleted."}

