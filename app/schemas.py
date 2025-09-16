from pydantic import BaseModel
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

    class Config:
        from_attributes = True

