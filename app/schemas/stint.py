from pydantic import BaseModel, ConfigDict
from typing import Optional

# field for Stint
class StintBase(BaseModel):
    race_id: int
    session_id: int
    driver_number: int
    stint_number: int
    lap_start: Optional[int] = None
    lap_end: Optional[int] = None
    tyre_compound: Optional[str] = None

class StintCreate(StintBase):
    pass

class StintUpdate(BaseModel):
    lap_start: Optional[int] = None
    lap_end: Optional[int] = None
    tyre_compound: Optional[str] = None

class Stint(StintBase):
    stint_id: int

    model_config = ConfigDict(from_attributes=True)