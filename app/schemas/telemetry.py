from pydantic import BaseModel, ConfigDict
from typing import Optional

# field for Telemetry
class TelemetryBase(BaseModel):
    race_id: int
    session_id: int
    driver_number: int
    lap_number: int
    avg_speed: Optional[float] = None
    mean_rpm: Optional[float] = None
    median_gear: Optional[int] = None
    throttle_usage: Optional[float] = None
    brake_usage: Optional[float] = None
    drs_usage: Optional[int] = None

class TelemetryCreate(TelemetryBase):
    pass

class TelemetryUpdate(BaseModel):
    avg_speed: Optional[float] = None
    mean_rpm: Optional[float] = None
    median_gear: Optional[int] = None
    throttle_usage: Optional[float] = None
    brake_usage: Optional[float] = None
    drs_usage: Optional[int] = None

class Telemetry(TelemetryBase):
    telemetry_id: int

    class Config:
        model_config = ConfigDict(from_attributes=True)
