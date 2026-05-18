from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app import models, schemas

# return all weather from the database
def get_all_weather(db: Session):
    return db.query(models.Weather).all()

# return weather by weather_id if it exists
def get_weather_by_weather_id(db: Session, weather_id: int):
    weather = db.query(models.Weather).filter(models.Weather.weather_id == weather_id).first()
    if not weather:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Weather with weather_id='{weather_id}' is not found."
        )
    return weather

# create new weather in the database (unique per race_id and session_id)
def create_weather(db: Session, weather: schemas.WeatherCreate):
    weather_exists = db.query(models.Weather).filter(
        models.Weather.race_id == weather.race_id,
        models.Weather.session_id == weather.session_id
    ).first()

    if weather_exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Weather for race_id='{weather.race_id}' and session_id='{weather.session_id}' already exists."
        )

    db_weather = models.Weather(**weather.model_dump())
    db.add(db_weather)
    db.commit()
    db.refresh(db_weather)
    return db_weather

# update weather
def update_weather(db: Session, weather_id: int, weather_update: schemas.WeatherUpdate):
    weather_exists = db.query(models.Weather).filter(models.Weather.weather_id == weather_id).first()

    if not weather_exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Weather with weather_id='{weather_id}' is not found."
        )

    update_data = weather_update.model_dump()
    for field, value in update_data.items():
        if value is not None:
            setattr(weather_exists, field, value)

    db.commit()
    db.refresh(weather_exists)
    return weather_exists

# delete weather
def delete_weather(db: Session, weather_id: int):
    weather_exists = db.query(models.Weather).filter(models.Weather.weather_id == weather_id).first()
    if not weather_exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Weather with weather_id='{weather_id}' is not found."
        )
    db.delete(weather_exists)
    db.commit()
    return {"detail": f"Weather '{weather_id}' is deleted."}