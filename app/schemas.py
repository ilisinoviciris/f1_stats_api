from pydantic import BaseModel, ConfigDict
from typing import Optional

# fields for Driver
class DriverBase(BaseModel):
    full_name: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    driver_number: int
    name_acronym: Optional[str] = None
    team_name: Optional[str] = None
    country_code: Optional[str] = None

# fields to create a new driver
class DriverCreate(DriverBase):
    driver_id: str

# fields for updating a driver (all fields are optional)
class DriverUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    driver_number: Optional[int] = None
    name_acronym: Optional[str] = None
    team_name: Optional[str] = None
    country_code: Optional[str] = None  

# fields returned
class Driver(DriverBase):
    driver_id: str

    model_config = ConfigDict(from_attributes=True)

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