from pydantic import BaseModel, ConfigDict
from typing import Optional

# field for Telemetry
class TelemetryBase(BaseModel):
    race_id: int
    session_id: int
    driver_number: int
    lap_number: int
    speed_avg: Optional[float] = None
    rpm_mean: Optional[float] = None
    gear_mean: Optional[int] = None
    throttle_mean: Optional[float] = None
    brake_usage: Optional[float] = None
    drs_usage: Optional[int] = None
    time: Optional[float] = None

class TelemetryCreate(TelemetryBase):
    pass

class TelemetryUpdate(BaseModel):
    speed_avg: Optional[float] = None
    rpm_mean: Optional[float] = None
    gear_mean: Optional[int] = None
    throttle_mean: Optional[float] = None
    brake_usage: Optional[float] = None
    drs_usage: Optional[int] = None
    time: Optional[float] = None

class Telemetry(TelemetryBase):
    telemetry_id: int

    class Config:
        model_config = ConfigDict(from_attributes=True)
