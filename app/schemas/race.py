from pydantic import BaseModel, ConfigDict
from typing import Optional

# field for Race
class RaceBase(BaseModel):
    race_id: int
    race_name: str
    circuit_name: str
    location: str
    country_name: str
    year: int

class RaceCreate(RaceBase):
    race_id: int

class RaceUpdate(BaseModel):
    race_name: Optional[str] = None
    circuit_name: Optional[str] = None
    location: Optional[str] = None
    country_name: Optional[str] = None
    year: Optional[int] = None

class Race(RaceBase):
    race_id: int

    model_config = ConfigDict(from_attributes=True)