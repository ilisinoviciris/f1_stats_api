from sqlalchemy.orm import declarative_base

Base = declarative_base()

from .driver import Driver
from .race import Race
from .lap import Lap
from .session import Session
from .stint import Stint
from .telemetry import Telemetry

__all__ = ["Driver", "Race", "Lap", "Session", "Stint", "Telemetry"]