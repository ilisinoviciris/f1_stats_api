from pydantic import BaseModel, ConfigDict
from typing import Optional


# field for Weather
class WeatherBase(BaseModel):
    race_id: int
    session_id: int
    air_temp: Optional[float] = None
    track_temp: Optional[float] = None
    humidity: Optional[float] = None
    pressure: Optional[float] = None
    wind_speed: Optional[float] = None
    rainfall: Optional[float] = None

class WeatherCreate(WeatherBase):
    pass

class WeatherUpdate(BaseModel):
    air_temp: Optional[float] = None
    track_temp: Optional[float] = None
    humidity: Optional[float] = None
    pressure: Optional[float] = None
    wind_speed: Optional[float] = None
    rainfall: Optional[float] = None

class Weather(WeatherBase):
    weather_id: int

    class Config:
        model_config = ConfigDict(from_attributes=True)