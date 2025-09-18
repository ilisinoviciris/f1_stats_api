from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app import models, schemas

# return all races from the database
def get_all_races(db: Session):
    return db.query(models.Race).all()

# return a race by race_id if it exists
def get_race_by_race_id(db: Session, race_id: int):
    race = db.query(models.Race).filter(models.Race.race_id == race_id).first()
    if not race:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Race with race_id='{race_id}' is not found."
        )
    return race

# create a new race in the database (if race_id doesn't already exist)
def create_race(db: Session, race: schemas.RaceCreate):
    race_exists = db.query(models.Race).filter(models.Race.race_id == race.race_id).first()
    if race_exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=f"Race with this race_id='{race.race_id}' already exists."
            )
    
    db_race = models.Race(**race.model_dump())
    db.add(db_race)
    db.commit()
    db.refresh(db_race)
    return db_race

# update a race
def update_race(db: Session, race_id: int, race_update: schemas.RaceUpdate):
    race_exists = db.query(models.Race).filter(models.Race.race_id == race_id).first()
    if not race_exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Race with this race_id='{race_id}' is not found."
        )

    update_data = race_update.model_dump()
    for field, value in update_data.items():
        if value is not None:
            setattr(race_exists, field, value)

    db.commit()
    db.refresh(race_exists)
    return race_exists
    
# delete a race
def delete_race(db: Session, race_id: int):
    race_exists = db.query(models.Race).filter(models.Race.race_id == race_id).first()
    if not race_exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Race with this race_id='{race_id}' is not found."
        )
    db.delete(race_exists)
    db.commit()
    return {"detail": f"Race '{race_id}' is deleted."}

