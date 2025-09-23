from sqlalchemy.orm import declarative_base

Base = declarative_base()

from .driver import Driver
from .race import Race
from .lap import Lap
from .session import Session

__all__ = ["Driver", "Race", "Lap", "Session"]