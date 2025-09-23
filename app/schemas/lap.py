from pydantic import BaseModel, ConfigDict
from typing import Optional

# fields for Lap
class LapBase(BaseModel):
    race_id: int
    session_id: int
    driver_number: int
    lap_number: int
    lap_duration: Optional[float] = None
    duration_sector_1: Optional[float] = None
    duration_sector_2: Optional[float] = None
    duration_sector_3: Optional[float] = None
    i1_speed: Optional[float] = None
    i2_speed: Optional[float] = None
    st_speed: Optional[float] = None
    is_pit_out_lap: Optional[bool] = None

# fields to create a new lap
class LapCreate(LapBase):
    pass

# fields for updating a driver (all fields are optional)
class LapUpdate(BaseModel):
    lap_duration: Optional[float] = None
    duration_sector_1: Optional[float] = None
    duration_sector_2: Optional[float] = None
    duration_sector_3: Optional[float] = None
    i1_speed: Optional[float] = None
    i2_speed: Optional[float] = None
    st_speed: Optional[float] = None
    is_pit_out_lap: Optional[bool] = None

# fields returned
class Lap(LapBase):
    lap_id: int

    model_config = ConfigDict(from_attributes=True)
