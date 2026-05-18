from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app import schemas, database
from app.repositories import weather_repository
import httpx

# initializing router 
router = APIRouter(prefix="/weather", tags=["Weather"])

# dependency for the database
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# endpoint for retrieving all weather data -> GET /weather/
@router.get("/", response_model=List[schemas.Weather])
def get_all_weather(db: Session = Depends(get_db)):
    return weather_repository.get_all_weather(db)

# endpoint for retrieving weather by weather_id -> GET /weather/{id}
@router.get("/{weather_id}", response_model=schemas.Weather)
def get_weather_by_id(weather_id: int, db: Session = Depends(get_db)):
    return weather_repository.get_weather_by_weather_id(db, weather_id)

# endpoint for creating a new weather record -> POST /weather/
@router.post("/", response_model=schemas.Weather, status_code=201)
def create_weather(weather: schemas.WeatherCreate, db: Session = Depends(get_db)):
    return weather_repository.create_weather(db, weather)

# endpoint for updating weather -> PUT /weather/{id}
@router.put("/{weather_id}", response_model=schemas.Weather)
def update_weather(weather_id: int, weather: schemas.WeatherUpdate, db: Session = Depends(get_db)):
    return weather_repository.update_weather(db, weather_id, weather)

# endpoint for deleting weather -> DELETE /weather/{id}
@router.delete("/{weather_id}")
def delete_weather(weather_id: int, db: Session = Depends(get_db)):
    return weather_repository.delete_weather(db, weather_id)